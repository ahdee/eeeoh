    $(function() {
      
     
      $('a#calculate').bind('click', function() {
        $.getJSON('/go', {
          a: $('input[name="a"]').val(),
          b: $('input[name="b"]').val()
        }, function(data) {
          $("#result").text(data.result);
        });
        return false;
      });
      
      $('a#calculate2').bind('click', function() {
        $.getJSON('/go', {
          a: $('input[name="a"]').val(),
          b: $('input[name="b"]').val()
        }, function(data) {
          $("#result").text(data.result);
        });
        return false; });
      
});


function checkFilled(e) {
	var inputVal = document.getElementById(e.id);
    if (inputVal.value == 0) {
        inputVal.style.backgroundColor = "yellow";
    }
    else{
        inputVal.style.backgroundColor = "red";
    }
}
