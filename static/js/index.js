function yesnoCheck() {
    if (document.getElementById('limit').checked) {
        document.getElementById('ifYes').style.display = 'block';
    } else document.getElementById('ifYes').style.display = 'none';

}

function refreshTable() {
    $.ajax({
        url: '/update_price',
        type: 'GET',
        dataType: 'json',
        success: function (response) {
            $('#refresh').html(response.html_response);
        },
        complete: function (response) {
            setTimeout(refreshTable, 30000);
        }
    });
}


$(document).ready(function () {
    $('.cancelorder').click(function () {
        var order_id = $(this).data('id');
        $.ajax({
            url: '/cancelorder',
            type: 'post',
            data: {order_id: order_id},
            success: function (data) {
                console.log("Order canceled");
                Swal.fire({
                        title: 'Order Cancelled',
                        html: '',
                        timer: 1000
                    });
            }
        });

    });

    $('.buysell').click(function () {
        var stock_id = $(this).data('id');
        $.ajax({
            url: '/markettimecheck',
            type: 'GET',
            dataType: 'json',
            success: function (response) {
                if (response.market_time) {
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
                } else {
                    Swal.fire({
                        title: 'Market Closed!',
                        html: 'Cannot place orders',
                        timer: 2000,
                        timerProgressBar: true,
                    });
                }
            },
        });

    });

    setTimeout(refreshTable, 30000);

});
