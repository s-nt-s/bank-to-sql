const DFL_RGB_COLOR = {
  red: {
    backgroundColor: "rgba(255, 99, 132, 0.2)",
    borderColor: "rgba(255, 99, 132, 1)",
  },
  blue: {
    backgroundColor: "rgba(54, 162, 235, 0.2)",
    borderColor: "rgba(54, 162, 235, 1)",
  },
  green: {
    backgroundColor: "rgb(60, 255, 60, 0.2)",
    borderColor: "rgb(60, 255, 60)",
  },
  yellow: {
    backgroundColor: "rgb(255,255,0, 0.2)",
    borderColor: "rgb(255,255,0)",
  },
  grey: {
    backgroundColor: "rgb(211,211,211, 0.2)",
    borderColor: "rgb(211,211,211)",
  },
};

function getCanvas(id) {
  let n = $.i(id);
  if (n == null) {
    console.error("#" + id + " no encontrado");
    return null;
  }
  if (n.tagName == "CANVAS") return n;
  const cnvs = n.getElementsByTagName("canvas");
  if (cnvs.length == 1) return cnvs[0];
  if (cnvs.length > 1) {
    console.error("#" + id + " canvas da demasiados resultados");
    return null;
  }
  console.debug("Se crea <canvas> en #" + id);
  n.insertAdjacentHTML("beforeend", "<canvas></canvas>");
  return n.getElementsByTagName("canvas")[0];
}

function frmtEur(n) {
  return n.toLocaleString("es-ES", {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
    useGrouping: "always",
  });
}


function getMode(arr) {
  const frecuencias = {};
  let maxFrecuencia = 0;
  let moda = null;

  for (const num of arr) {
    frecuencias[num] = (frecuencias[num] || 0) + 1;
  }

  for (const num in frecuencias) {
    if (frecuencias[num] > maxFrecuencia) {
      maxFrecuencia = frecuencias[num];
      moda = num;
    }
  }

  return moda;
}

function setChart(id, data) {
  const ctx = getCanvas(id);
  if (ctx == null) return null;
  const chrt = Chart.getChart(ctx);
  const isMiles = data!=null && (data.datasets.filter(d=>getMode(d.data)<1000).length==0);
  const yCallback = !isMiles?frmtEur:(v)=>frmtEur(v/1000).replace("€", "k€");
  if (chrt == null) {
    if (data == null) return;
    new Chart(ctx, {
      type: "line",
      data: data,
      options: {
        interaction: {
          mode: "index",
          intersect: false,
        },
        scales: {
          y: {
            ticks: {
              stepSize: isMiles? 1000: null,
              callback: yCallback,
            },
          },
        },
        plugins: {
          tooltip: {
            titleAlign: 'center',
            bodyAlign: 'right',
            titleFont: {
              family: "monospace"
            },
            bodyFont: {
              family: "monospace"
            },
            footerFont: {
              family: "monospace"
            },
            callbacks: {
              label: (context) => ' '+frmtEur(context.raw),
            }
          },
        },
      }
    });
    return;
  }
  if (data == null) {
    chrt.destroy();
    return;
  }
  chrt.data = data;
  chrt.options.scales.y.ticks.stepSize = isMiles? 1000: null;
  chrt.options.scales.y.ticks.callback = yCallback;
  chrt.update();
}
