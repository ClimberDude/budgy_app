/*jslint browser: true*/
/*global $*/

$(document).ready(function () {
    $('#serverside_table').DataTable({
        bProcessing: true,
        bServerSide: true,
        sPaginationType: "full_numbers",
        lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
        bjQueryUI: true,
        sAjaxSource: '/retr_trans_select',
        order: [[1, 'desc']],
        columns: [
        {"data": "Select"},
        {"data": "Date"},
        {"data": "Amount"},
        {"data": "Type"},
        {"data": "Budget Category"},
        {"data": "Vendor"},
        {"data": "Note"}
        ],
        columnDefs:[{
            targets: 0,
            searchable: false,
            orderable: false,
            render: function(data, type, full, meta){
               if(type === 'display'){
                  data = '<input id="select_trans" name="select_trans" type="radio" value="' + data + '">';
               }
               return data;
            }
        },{
            targets: 2,
            searchable: true,
            orderable: true,
            render: function(data, type, full, meta){
               return '$ '+data.toFixed(2);
            }
        }]
    });
});