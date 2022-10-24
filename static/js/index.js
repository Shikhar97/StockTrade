function yesnoCheck() {
    if (document.getElementById('limit').checked) {
        document.getElementById('ifYes').style.display = 'block';
    } else document.getElementById('ifYes').style.display = 'none';

}

function buysell(stock_id) {
    $.ajax({
        url: '/markettimecheck',
        type: 'GET',
        dataType: 'json',
        success: function (response) {
            if (response.market_time) {
                $.ajax({
                    url: '/buysell/'+ stock_id,
                    type: 'POST',
                    // data: {stock_id: stock_id},
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

}
$('.cancelorder').click(function () {
        var order_id = $(this).data('id');
        $.ajax({
            url: '/cancelorder',
            type: 'POST',
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

function refreshTable() {
    $.ajax({
        url: '/update_price',
        type: 'GET',
        dataType: 'json',
        success: function (response) {
            $("#refresh").html(response.html_response);
        },
        complete: function (response) {
            setTimeout(refreshTable, 5000);
        }
    });
}

$(document).ready(function () {
    setTimeout(refreshTable, 5000);
});
