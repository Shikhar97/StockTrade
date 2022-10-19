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
    $('.userinfo').click(function(){
              var stock_id = $(this).data('id');
              $.ajax({
                url: '/buysell',
                type: 'post',
                data: {id: stock_id},
                success: function(data){
                    $('.modal-body').html(data);
                    $('.modal-body').append(data.htmlresponse);
                    $('#empModal').modal('show');
                }
            });
          });
    $(document).on('click', '.refresher', function () {
        $.ajax({
            url: '/',
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