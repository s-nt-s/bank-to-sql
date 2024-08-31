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


function calStepSize(datasets, chart) {
  if (chart !=null) datasets = chart.data.datasets;
  const vals = datasets.flatMap((dataset, i) => {
    if (chart!=null && !chart.isDatasetVisible(i)) return [];
      return dataset.data;
  });
  const length = vals.length / datasets.length;

  let s;
  const steps = [10000, 1000];
  for (let i = 0; i < steps.length; i++) {
    s = steps[i];
    if (vals.filter((v) => v > s).length > length) return s;
  }
  return null;
}

function getCtxIfNeedCreate(id, data) {
  const ctx = getCanvas(id);
  if (ctx == null) return null;
  const chrt = Chart.getChart(ctx);
  if (chrt == null) return data!=null?ctx:null;
  if (data == null) {
    chrt.destroy();
    return null;
  }
  chrt.data = data;
  chrt.update();
  return null;
}

function setLineChart(id, data, onClick) {
  const ctx = getCtxIfNeedCreate(id, data);
  if (ctx == null) return;
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
            stepSize: calStepSize(data.datasets),
            callback: function (value, index, values) {
              const yScale = this.chart.scales.y;
              const stepSize = yScale.options.ticks.stepSize;
              if (stepSize==null || stepSize<1000 || (stepSize%1000)!=0) return frmtEur(value);
              return frmtEur(value/1000).replace("€", "k€");
            }
          },
        },
      },
      plugins: {
        tooltip: {
          titleAlign: "center",
          bodyAlign: "right",
          titleFont: {
            family: "monospace",
          },
          bodyFont: {
            family: "monospace",
          },
          footerFont: {
            family: "monospace",
          },
          callbacks: {
            label: (context) => " " + frmtEur(context.raw),
          },
        },
        legend: {
          onClick: (e, legendItem, legend) => {
            const index = legendItem.datasetIndex;
            const ci = legend.chart;
            const meta = ci.getDatasetMeta(index);

            meta.hidden = meta.hidden === null ? !ci.data.datasets[index].hidden : null;

            ci.options.scales.y.ticks.stepSize = calStepSize(ci.data.datasets, ci);

            ci.update();
          },
        },
      },
      onClick: onClick
    },
  });
}


function setPieChart(id, data) {
  const ctx = getCtxIfNeedCreate(id, data);
  if (ctx == null) return;
  data.datasets.forEach(d => {
    if (d.backgroundColor!=null) return;
    if (d.data.length<=7) return;
    d.backgroundColor = generateColors(d.data.length);
  });
  new Chart(ctx, {
    type: "pie",
    data: data,
    options: {
      plugins: {
        tooltip: {
          callbacks: {
            label: (context) => {
              //const label = context.label;
              const value = context.raw;
              const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
              const percent = ((value / total) * 100).toFixed(2);
              return frmtEur(value) + " (" + percent + "%)";
            },
          },
        }
      },
    },
  });
}


function generateColors(numColors) {
  const colors = [];
  for (let i = 0; i < numColors; i++) {
      const color = `hsl(${i * 360 / numColors}, 100%, 50%)`;
      colors.push(color);
  }
  return colors;
}