$(document).on('click', '.navbar-nav li', function() {
       $(".navbar-nav li").removeClass("active");
       $(this).addClass("active");
   });

// $("ul li").click(function() {
//     $("ul .active").removeClass("active");
//     $(this).addClass("active");
// });
