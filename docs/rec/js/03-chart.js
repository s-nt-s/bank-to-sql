const DFL_RGB_COLOR={
    "red": {
      backgroundColor: 'rgba(255, 99, 132, 0.2)',
      borderColor: 'rgba(255, 99, 132, 1)'
    },
    "blue": {
      backgroundColor: 'rgba(54, 162, 235, 0.2)',
      borderColor: 'rgba(54, 162, 235, 1)',
    },
    "green": {
      backgroundColor: "rgb(60, 255, 60, 0.2)",
      borderColor: "rgb(60, 255, 60)"
    },
    "yellow": {
      backgroundColor: "rgb(255,255,0, 0.2)",
      borderColor: "rgb(255,255,0)"
    },
    "grey": {
      backgroundColor: "rgb(211,211,211, 0.2)",
      borderColor: "rgb(211,211,211)"
    }
  }

function getCanvas(id) {
    let n = $.i(id);
    if (n == null) {
        console.error("#"+id+" no encontrado");
        return null;
    }
    if (n.tagName == "CANVAS") return n;
    const cnvs = n.getElementsByTagName("canvas");
    if (cnvs.length==1) return cnvs[0];
    if (cnvs.length>1) {
        console.error("#"+id+" canvas da demasiados resultados");
        return null;
    }
    console.debug("Se crea <canvas> en #"+id);
    n.insertAdjacentHTML('beforeend', '<canvas></canvas>');
    return n.getElementsByTagName("canvas")[0];
}

function setChart(id, data) {
    const ctx = getCanvas(id);
    if (ctx == null) return null;
    console.log(data)
    const chrt = Chart.getChart(ctx);
    if (chrt == null) {
        new Chart(ctx, {
            type: 'line',
            data: data
        });
        return;
    }
    chrt.data = data;
    chrt.update();
}