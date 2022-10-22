function yesnoCheck() {
    if (document.getElementById('limit').checked) {
        document.getElementById('ifYes').style.display = 'block';
    } else document.getElementById('ifYes').style.display = 'none';

}


 function refreshTable(){
        $.ajax({
            url: '/update_price',
            type: 'GET',
            dataType: 'json',
            success: function(response) {
                $('#refresh').html(response.html_response);
            },
            complete:function(response){
                setTimeout(refreshTable,10000);
            }
        });
    }
function checkmarket(){
        $.ajax({
            url: '/markettimecheck',
            type: 'GET',
            dataType: 'json',
            success: function(response) {
                $('#refresh').html(response.time_response);
            },
        complete:function(response){
            setTimeout(checkmarket,10000);
           }
        });
}

$(document).ready(function () {
    
    $('.userinfo').click(function () {
        var stock_id = $(this).data('id');
        $.ajax({
            url: '/buysell',
            type: 'post',
            data: {id: stock_id},
            success: function (data) {
                $('.modal-body').html(data);
                $('.modal-body').append(data.htmlresponse);
                $('#empModal').modal('show');
            }
        });
    });

   




    // setInterval(refreshTable, 10000);
    // setInterval(checkmarket, 60000);
    setTimeout(checkmarket,2000);
    setTimeout(refreshTable,10000);
    
});
