{% extends 'base.php' %}

{% block title %}Admin Dashboard{% endblock %}

{% block script %}
<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
<script type="text/javascript">
      google.charts.load('current', {'packages':['corechart']});
      google.charts.setOnLoadCallback(drawChart);

      function drawChart() {
        var dataz = JSON.parse('{{ datas | tojson }}');
        var tambah;
        for(let i = 0; i < dataz.length; i++){
            if(i==0){
                tambah = "["+dataz[i]+"],";
            }else{
                tambah += "["+dataz[i]+"],";
            }
        }
        //document.write(tambah);
        <?php
          $data = json_decode('{{datas}}');
          echo $data;
        ?>
        var data = google.visualization.arrayToDataTable([
          ['Languages', 'Books'],
         
        // ['Work',     11],
        // ['Eat',      2],
        // ['Commute',  2],
        // ['Watch TV', 2],
        // ['Sleep',    7]
        ]);
        

        var options = {
          title: 'Students and their contribution'
        };

        var chart = new google.visualization.PieChart(document.getElementById('piechart'));

        chart.draw(data, options);
      }
 
    </script>
{% endblock %}

{% block content %}
<div id="piechart" style="width: 900px; height: 500px;"></div>
{% endblock %}