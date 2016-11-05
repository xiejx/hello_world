(function() {
	var my_array = new Array();
	var my_index = -1;  // 被点击的表头所在的位置
	var index_of_table = -1;  // 在哪个表格
	$(document).ready(function(){
		$("tr:odd").css("background-color","white");
		$("th").append("<img src='ascend.png', alt='ascend.png' />");
		$("th img").css("float","right");
		$("thead th").click(sort_table);
	});
	function sort_table() {
		var my_table = $(this).parents("table");  // 获取被点击元素所在的table
		if (index_of_table === my_table.index("table")&&my_index === my_table.find("thead th").index(this)) {
			my_array.reverse();
			change_img($(this));
		}
		else {to_array(this);}
		for (var i = 0; i < my_array.length; i++){my_table.children("tbody").append(my_array[i][1]);}
		set_color($(this));  // 设置颜色
	}
	function to_array(obj) {
		var my_table = $(obj).parents("table");
		$("th img").attr("src","ascend.png");
		index_of_table = my_table.index("table");
		my_index = my_table.find("thead th").index(obj);  // 位于该table的哪一列
		my_table.find("tbody tr").each(function(i) {
			my_array[i] = [$(this).children("td").eq(my_index).text(), this];
		});  // // 压入数组
		sort_array();// 对数组进行排序
	}
	function sort_array() {
		my_array.sort(function(a, b) {
			return a[0]>b[0];
		});
	}
	function change_img(obj) {
		if (obj.children().attr("src") === "ascend.png") {
			obj.children().attr("src","descend.png");
		} else {
			obj.children().attr("src","ascend.png");
		}
	}
	function set_color(obj) {
		$("th").css("background-color","#021b7b");  // 还原颜色
		obj.css("background-color","#a2affe");  // 设置被点击表头的颜色
		var my_table = obj.parents("table");
		my_table.find("tbody tr:odd").css("background-color","#dddddd");
		my_table.find("tbody tr:even").css("background-color","white");
	}
})();
