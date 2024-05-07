var hideAlert = sessionStorage.getItem("hideSiteAlert");
if (hideAlert === "true") {
	$("site-alert").hide();
}

$(document).ready(function() {
    $("site-alert .close").click(function(){
        sessionStorage.setItem("hideSiteAlert", "true");
        $("site-alert").hide();
    });
});


$(".sLymx1, .sLmx2").owlCarousel({
    items:1,
    loop:true,
	nav: true,
    margin:10,
    autoplay:true,
    autoplayTimeout:2500,
    autoplayHoverPause:true
});

$(".sLymx3").owlCarousel({
    items:4,
    loop:true,
	nav: false,
	dots:false,
    margin:10,
    autoplay:true,
    autoplayTimeout:2500,
    autoplayHoverPause:true,
	responsiveClass:true,
	responsive : {
		0: {
			items: 4
		},
		768:{
			items: 5
		}
	}
});

$(".sLymx4").owlCarousel({
    items:2,
    loop:true,
    margin:10,
    autoplay:true,
    autoplayTimeout:2500,
    autoplayHoverPause:true
});