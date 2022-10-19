// document.addEventListener('DOMContentLoaded', ()=>{
// 	console.log("loaded")
// 	if(document.querySelector('#add_new')){
// 		document.querySelector('#add_new').onclick = function(){
// 			console.log("clicked")
// 			document.querySelector('#topdiv3').style.display = "none";
// 			document.querySelector('#topdiv2').style.display = "block";
// 		}
// 	}
// 	if(document.querySelector('#edit')){
// 		document.querySelector('#edit').onclick = function(){
// 			console.log("clicked")
// 			document.querySelector('#topdiv2').style.display = "none";
// 			document.querySelector('#topdiv3').style.display = "block";
// 		}
// 	}
// });
$(document).ready(function () {
    $(document).on('click', '.refresher', function () {
        $.ajax({
            url: 'ajax.php',
            method: get,
            dataType: 'json',
            success: function(response) {
                $('#table-to-refresh').html(response);
            }
        });
    });
});


document.getElementById('basicAlert').addEventListener('click', function () {
    Swal.fire(
        'Basic alert',
        'You clicked the button!'
    )
});