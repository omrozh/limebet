$(document).ready(function() {
	if ($(window).width() >= 768) desktop();
	if ($(window).width() < 768) mobile();
	
	function desktop()
	{
		new PerfectScrollbar(".match-cat", {
			wheelSpeed: 1,
			wheelPropagation: true
		});
		
		new PerfectScrollbar(".matchs", {
			wheelSpeed: 1,
			wheelPropagation: true
		});
		
		new PerfectScrollbar(".odds-sep", {
			wheelSpeed: 1,
			wheelPropagation: true
		});
		
		var calchHeight = $(".sportsbook .c2").height() - $(".sportsbook .c2 .c3").outerHeight() - $(".sportsbook .c2 .c4 .seTxs").outerHeight() - $(".sportsbook .c2 .c4 .matchshead").outerHeight() - 10;
		$(".matchs-cont").css("height", calchHeight + "px");
		
		var calchHeight2 = $(window).height() - $(".firsdt-cont").outerHeight() - $(".c3").outerHeight() - ($(".mybet .header").outerHeight() * 2) - 150;
		$(".odds-sep").css("max-height", calchHeight2 + "px");
		
		$(".match-items .spec-item .item-details").click(function(){
			var submenu = $(this).parent().find(".subitem2");
			var submenuElements = $(this).parent().find(".subitem2 a");
			if( submenuElements.length > 0 )
			{
				submenu.toggle();
				
				if( $(this).hasClass("active") )
					$(this).removeClass("active");
				else
					$(this).addClass("active");
			}
		});
		$(".match-items .item-details").click(function(){
			var submenu = $(this).parent().find(".subitem-cont");
			var submenuElements = $(this).parent().find(".subitem-cont .subitem");
			if( submenuElements.length > 0 )
			{
				submenu.toggle();
				
				if( $(this).hasClass("active") )
					$(this).removeClass("active");
				else
					$(this).addClass("active");
			}
		});
		$(".match-items .item .subitem-details").click(function(){
			var submenu = $(this).parent().find(".subitem2");
			var submenuElements = $(this).parent().find(".subitem2 a");
			if( submenuElements.length > 0 )
			{
				submenu.toggle();
				
				if( $(this).hasClass("active") )
					$(this).removeClass("active");
				else
					$(this).addClass("active");
			}
		});
		
		var mainContent = $(".mybet");
		var height = mainContent.height();
		mainContent.css("bottom", "-" + (height - 50) + "px");
		
		$(".mybet .header").click(function(){
			var mainContent = $(".mybet");
			var height = mainContent.height();
			
			if( mainContent.hasClass("active") )
			{
				mainContent.removeClass("active");
				mainContent.css("bottom", "-" + (height - 50) + "px");
			}
			else
			{
				mainContent.addClass("active");
				mainContent.css("bottom", "0");
			}
		});
		
		$(".c3 .sbms a:eq(0)").click(function() {
			$(".c2 .c4").show();
			$(".match-details").hide();
			
			$(".c3 .sbms a").removeClass("active");
			$(".c3 .sbms a:eq(0)").addClass("active");
		});
	}
	
	function mobile()
	{
		var owl = $(".mobileSlider");
		owl.owlCarousel({
			items:3,
			loop:true,
			nav: true,
			dots: false,
			center: true
		});
		
		var owl = $(".mobileSlider2");
		owl.owlCarousel({
			items:3,
			margin: 10,
			loop:true,
			nav: false,
			dots: false
		});
		
		$(".mybet-chart").click(function(){
			$(".mybet.mybet").show();
		});
		$(".mybet .header").click(function(){
			$(".mybet.mybet").hide();
		});
	}
	
	$(".odds-cat .cats button").click(function(){
		var target = $(this).attr("id");
		
		$(".odds-cat .cats button").removeClass("active");
		$(this).addClass("active");
		
		$(".odds-list").hide();
		$(".odds-sep ." + target).show();
	});
	
	$(".mtchdtls .match").click(function() {
		$(".sportsbook .c2 .c4").hide();
		$(".sportsbook .match-details").show();
		
		$(".sportsbook .c3 .sbms a").removeClass("active");
		$(".sportsbook .c3 .sbms a:eq(1)").addClass("active");
	});
});
	
