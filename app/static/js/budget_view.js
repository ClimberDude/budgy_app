/*jslint browser: true*/
/*global $*/

$(document).ready(function () {
    $('#serverside_table').DataTable({
        bProcessing: true,
        bServerSide: true,
        sPaginationType: "full_numbers",
        lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
        bjQueryUI: true,
        sAjaxSource: '/retr_budget_view',
        order: [[0, 'asc']],
        columns: [
        {"data": "Category Title"},
        {"data": "Spending Category"},
        {"data": "Annual Budget"},
        {"data": "Current Balance"}
        ],
        columnDefs:[{
            targets: [2,3],
            searchable: true,
            orderable: true,
            render: function(data, type, full, meta){
               return '$ '+data.toFixed(2);
            }
        }]
    });
});