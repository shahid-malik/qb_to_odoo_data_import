$(document).ready(function(){
    if($('.is_sample_order').is(":checked")){
        $("#btn_visible").show();
        $("a[href$='/shop/checkout?express=1']").attr("style", "display: none !important");
      }
      else{
        $("#btn_visible").attr("style", "display: none !important");
        $("a[href$='/shop/checkout?express=1']").show()
      }
    $('.is_sample_order').click(function(){
      if($(this).is(":checked")){
        $("#btn_visible").show();
        $("a[href$='/shop/checkout?express=1']").attr("style", "display: none !important");
      }
      else if($(this).is(":not(:checked)")){
        $("#btn_visible").attr("style", "display: none !important");
        $("a[href$='/shop/checkout?express=1']").show()
      }
      });
});