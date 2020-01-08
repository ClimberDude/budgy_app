/*jslint browser: true*/
/*global $*/

$(document).ready(function () {
    $('#serverside_table').DataTable({
        bProcessing: true,
        bServerSide: true,
        sPaginationType: "full_numbers",
        lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
        bjQueryUI: true,
        sAjaxSource: '/retr_trans_view',
        order: [[0, 'desc']],
        columns: [
        {"data": "Date"},
        {"data": "Amount"},
        {"data": "Type"},
        {"data": "Budget Category"},
        {"data": "Vendor"},
        {"data": "Note"}
        ],
        columnDefs:[{
            targets: 1,
            searchable: true,
            orderable: true,
            render: function(data, type, full, meta){
               return '$ '+data.toFixed(2);
            }
        }]
    });
});
