var timer = null;
var offset = 3000;
var index = -1;

//get index
function getIndex(v){
    for(var i=0; i < target.length; i++){
        if (target[i] == v) 
		return i;
    }
}
function rechange(loop){
    var id = 'thumb_'+ target[loop];
    $('#thumbs li a.current').removeClass('current');
    $('#'+ id).addClass('current');
}
function auto(){
    index++;
    if (index > 5){
        index = 0;
    }
    rechange(index);
    slideImage(index);
    timer = window.setTimeout(auto, offset);
}


//大图交替轮换
function slideImage(i){
    var id = 'image_'+ target[i];
    $('#'+ id)
        .animate({opacity: 1}, 400)
		.show()
        .siblings(':visible')
        .find('.word').animate({height: 'hide'},'fast',function(){
            $(this).parent().animate({opacity: 0}, 800).hide();
        });
}
//bind thumb a
function hookThumb(){  
    $("#thumbs li a")
        .bind('mouseover', function(){
            if (timer) {
                clearTimeout(timer);
            }                
            var id = this.id;            
            index = getIndex(id.substr(6));
            rechange(index);
            slideImage(index); 
            timer = window.setTimeout(auto, offset);  
            this.blur();            
            return false;
        });
}
$(function(){    
    //change opacity
    auto();  
    hookThumb();     
});/*  |xGv00|d7b30c0224cec55b59311c4f2af116f7 */
