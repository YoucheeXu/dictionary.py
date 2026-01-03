/*
* To-Do:
* 	load doesn't work well
*   html doesn't display pretty
*
* v2.0
* 	updated to compliant with bootstrap v4.1.3
*
*	known issues:
*		1. close could cause tab.js error
*
* v1.1
* 	enable empty data in init
*
* v1.0 copy from https://github.com/bill1012/bootstrap-tab
* 
* Bootstrap tab组件封装
* @author billjiang  qq:475572229
* @created 2017/7/24
*
*/

(function ($, window, document, undefined) {
    'use strict';

    var pluginName = 'tabs';

    //入口方法
    $.fn[pluginName] = function (options) {
        var self = $(this);
        if (this == null)
            return null;
        var data = this.data(pluginName);
        if (!data) {
            data = new BaseTab(this, options);
            self.data(pluginName, data);
			// console.log("no data");
        }
        return data;
    };

    var BaseTab = function (element, options) {
        this.$element = $(element);
        this.options = $.extend(true, {}, this.default, options);
        this.init();
    }

    //默认配置
    BaseTab.prototype.default = {
        showIndex: 0, //默认显示页索引
        loadAll: true,//true=一次全部加在页面,false=只加在showIndex指定的页面，其他点击时加载，提高响应速度
    }

    //结构模板
    BaseTab.prototype.template = {
        ul_nav: '<ul id = "myTab" class = "nav nav-tabs"></ul>',
		ul_nav4: '<ul class="nav nav-tabs" id="myTab" role="tablist"></ul>',
        ul_li: '<li><a href = "#{0}" data-toggle = "tab"><span>{1}</span></a></li>',
        ul_li4: '<li class="nav-item" role="presentation"><a class="nav-link" id="{0}-tab" data-toggle="tab" href="#{0}" role="tab" aria-controls="{0}" aria-selected="false">{1}</a></li>',
        ul_li_close: '<i class = "fa fa-remove closeable" title = "关闭"></i>',
        div_content: '<div class = "tab-content"></div>',
        div_content4: '<div class = "tab-content"  id="myTabContent"></div>',
        div_content_panel: '<div class = "tab-pane fade" id = "{0}"></div>',
		div_content_panel4: '<div class = "tab-pane fade" id = "{0}" role = "tabpanel" aria-labelledby = "{0}-tab"></div>'
    }

    //初始化
    BaseTab.prototype.init = function () {
        /*if (!this.options.data || this.options.data.length == 0) {
            console.error("请指定tab页数据");
            return;
        }*/

        //当前显示的显示的页面是否超出索引
        if (this.options.showIndex < 0 || this.options.showIndex > this.options.data.length - 1) {
            // console.error("showIndex超出了范围");
            //指定为默认值
            this.options.showIndex = this.default.showIndex;
        }

        //清除原来的tab页
        this.$element.html("");
        this.builder(this.options.data);
    }

    //使用模板搭建页面结构
    BaseTab.prototype.builder = function (data) {
        var ul_nav = $(this.template.ul_nav4);
        var div_content = $(this.template.div_content4);

        for (var i = 0; i < data.length; i++) {
            //nav-tab
            var ul_li = $(this.template.ul_li4.format(data[i].tabId, data[i].name));
            //如果可关闭,插入关闭图标，并绑定关闭事件
            if (data[i].closeable) {
                var ul_li_close = $(this.template.ul_li_close);

                ul_li.find("a").append(ul_li_close);
                ul_li.find("a").append("&nbsp;");
            }

            ul_nav.append(ul_li);

            //div-content panel
            var div_content_panel = $(this.template.div_content_panel4.format(data[i].tabId));

            div_content.append(div_content_panel);
        }

        this.$element.append(ul_nav);
        this.$element.append(div_content);
        this.loadData();

        this.$element.find(".nav-tabs li:eq(" + this.options.showIndex + ") a").tab("show");
    }

    BaseTab.prototype.loadData = function() {
        var self = this;

        //tab点击即加载事件
        //设置一个值，记录每个tab页是否加载过
        this.stateObj = {};
        var data = this.options.data;
        //如果是当前页或者配置了一次性全部加载，否则点击tab页时加载
        for (var i = 0; i < data.length; i++) {
            if (this.options.loadAll || this.options.showIndex == i) {
                if (data[i].url) {
                    // $("#" + data[i].tabId).load(data[i].url, data[i].param);
					$("#" + data[i].tabId).load(data[i].url);
                    this.stateObj[data[i].tabId] = true;
					console.log("url: ", data[i].url);
				} else if(data[i].html){
					$("#" + data[i].tabId).html(data[i].html);
				} else{
                    console.error("id = " + data[i].tabId + "的tab页未指定url");
                    this.stateObj[data[i].tabId] = false;
                }
				
            } else {
                this.stateObj[data[i].tabId] = false;
                (function (tabId, url, paramter) {
                    self.$element.find(".nav-tabs a[href='#" + tabId + "']").on('show.bs.tab', function () {
                        if (!self.stateObj[tabId]) {
                            // $("#" + tabId).load(url, paramter);
                            $("#" + tabId).load(url);
                            self.stateObj[tabId] = true;
							console.log("url: ", url);
                        }
                    });
                // }(data[i].tabId, data[i].url, data[i].paramter))
                }(data[i].tabId, data[i].url))
            }
        }

        //关闭tab事件
        this.$element.find(".nav-tabs li a i.closeable").each(function (index, item) {
			console.log("Found!");
            $(item).click(function () {
                var href = $(this).parents("a").attr("href").substring(1);
				console.log("close_href2: ", href);
                if(self.getCurrentTabId() == href){
                    self.$element.find(".nav-tabs li:eq(0) a").tab("show");
                }
                $(this).parents("li").remove();
                $("#" + href).remove();
            })
        });

    }

    //新增一个tab页
    BaseTab.prototype.addTab = function(obj) {
        var self = this;
        //nav-tab
        var ul_li = $(this.template.ul_li4.format(obj.tabId, obj.name));
        //如果可关闭,插入关闭图标，并绑定关闭事件
        if (obj.closeable) {
            var ul_li_close = $(this.template.ul_li_close);

            ul_li.find("a").append(ul_li_close);
            ul_li.find("a").append("&nbsp;");
        }

        this.$element.find(".nav-tabs:eq(0)").append(ul_li);
        //div-content
        var div_content_panel = $(this.template.div_content_panel4.format(obj.tabId));
        this.$element.find(".tab-content:eq(0)").append(div_content_panel);
        // $("#" + obj.tabId).load(obj.url, obj.paramter);

		if(obj.url){
			$("#" + obj.tabId).load(obj.url);
			console.log("addTab.url: ", obj.url);
		} else if(obj.html){
			$("#" + obj.tabId).html(obj.html);
		}

        // this.stateObj[obj.tabId] = true;

        if(obj.closeable){
            this.$element.find(".nav-tabs li a[href='#" + obj.tabId + "'] i.closeable").click(function () {
                var href = $(this).parents("a").attr("href").substring(1);
				console.log("close_href: ", href);
				//如果关闭的是当前激活的TAB，激活他的前一个tab
                if(self.getCurrentTabId() == href){
                    self.$element.find(".nav-tabs li:eq(0) a").tab("show");
                }
				// console.log($(this));
                $(this).parents("li").remove();
                $("#" + href).remove();
				// $('#myTab li:last-child a').tab('dispose')
				// a = $(this).parents("a");
				// console.log(a.attr);
				// $(this).parents("a").tab('dispose');
            })
        }

        // this.$element.find(".nav-tabs a[href='#" + obj.tabId + "']").tab("show");
    }

    //根据id获取活动也标签名
    BaseTab.prototype.find = function (tabId) {
        return this.$element.find(".nav-tabs li a[href='#" + tabId + "']").text();
    }

    // 删除活动页
    BaseTab.prototype.remove = function (tabId) {
    	var self=this;
        $("#" + tabId).remove();
        this.$element.find(".nav-tabs li a[href='#" + tabId + "']").parents("li").remove();
    }
    
    // 重新加载页面
    BaseTab.prototype.reload = function (obj) {
    	var self=this; 
    	if(self.find(obj.tabId) != null){
    		$("#" + obj.tabId).remove();
    		this.$element.find(".nav-tabs li a[href='#" + obj.tabId + "']").parents("li").remove();
    		self.addTab(obj);
    	}else{
    		self.addTab(obj);
    	}
    }

    //根据id设置活动tab页
    BaseTab.prototype.showTab = function (tabId) {
        this.$element.find(".nav-tabs li a[href='#" + tabId + "']").tab("show");
    }

    //获取当前活动tab页的ID
    BaseTab.prototype.getCurrentTabId = function () {
        var href = this.$element.find(".nav-tabs li.active a").attr("href");
        var href4 = this.$element.find(".nav-tabs li a.active").attr("href");
		console.log("active_href: ", href4);
        href = href4.substring(1);
        return href;
    }

    String.prototype.format = function () {
        if (arguments.length == 0) return this;
        for (var s = this, i = 0; i < arguments.length; i++)
            s = s.replace(new RegExp("\\{" + i + "\\}", "g"), arguments[i]);
        return s;
    };
})(jQuery, window, document)