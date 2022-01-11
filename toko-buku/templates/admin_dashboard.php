{% extends 'base.php' %}
<?php
  $con = mysqli_connect("localhost","root","","toko_buku");
  if($con){
      echo "Connected";
  }
?>
{% block title %}Admin Dashboard{% endblock %}

{% block content %}
<html>
<head>
<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
<script type="text/javascript">
      google.charts.load('current', {'packages':['corechart']});
      google.charts.setOnLoadCallback(drawChart);

      function drawChart() {

        var data = google.visualization.arrayToDataTable([
          ['Languages', 'Books'],
        // ['Work',     11],
        // ['Eat',      2],
        // ['Commute',  2],
        // ['Watch TV', 2],
        // ['Sleep',    7]
        <?php
        $sql = "SELECT language, COUNT(*) FROM buku";
        $fire = mysqli_query($con, $sql);
        while ($result = mysqli_fetch_assoc($fire)) {
            echo"['".$result['Language']."',".$result['Books']."],";
        }
        ?>
        ]);
     
        var options = {
          title: 'Students and their contribution'
        };

        var chart = new google.visualization.PieChart(document.getElementById('piechart'));

        chart.draw(data, options);
      }
    </script>
    </head>
    <body>
    <div id="piechart" style="width: 900px; height: 500px;"></div>
  </body>
</html>
{% for genre in genre_list %}



{% endfor %}



{% endblock %}