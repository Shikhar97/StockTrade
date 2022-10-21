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
    setInterval(refreshTable, 10000);
});



function yesnoCheck() {
    if (document.getElementById('limit').checked) {
        document.getElementById('ifYes').style.display = 'block';
    } else document.getElementById('ifYes').style.display = 'none';

}

function refreshTable(){
        $.ajax({
            url: '/',
            type: 'GET',
            dataType: 'json',
            success: function(response) {
                $('#table-to-refresh').html(response);
            }
        });
    }


$(document).ready(function () {
    $('.editstock').click(function(){
              var stock_id = $(this).data('id');
              $.ajax({
                url: '/edit/stock_id',
                type: 'post',
                data: {id: stock_id},
                success: function(data){
                    $('.modal-body').html(data);
                    $('.modal-body').append(data.htmlresponse);
                    $('#empModal').modal('show');
                }
            });
          });
    setInterval(refreshTable, 10000);
});
