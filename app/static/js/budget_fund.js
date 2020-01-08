/*jslint browser: true*/
/*global $*/

$(document).ready(function () {
    $('#serverside_table').DataTable({
        bProcessing: true,
        bServerSide: true,
        sPaginationType: "full_numbers",
        lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
        bjQueryUI: true,
        sAjaxSource: '/retr_budget_select',
        order: [[1, 'asc']],
        columns: [
        {"data": "Select"},
        {"data": "Category Title"},
        {"data": "Spending Category"},
        {"data": "Annual Budget"},
        {"data": "Current Balance"}
        ],
        columnDefs:[{ 
            targets: 0,
            searchable: false,
            orderable: false,
            render: function(data, type, full, meta){
               if(type === 'display'){
                  data = '<input id="fund-budgets-fund_value" name="fund-budgets-fund_value" oninput="sumEntries()" type="text" value="">';      
               }
               return data;
            }
        },{
            targets: [3,4],
            searchable: true,
            orderable: true,
            render: function(data, type, full, meta){
               return '$ '+data.toFixed(2);
            }
        }]
    });
});