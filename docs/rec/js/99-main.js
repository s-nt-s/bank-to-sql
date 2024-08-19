INPUTS = "#ini, #fin, #cat input";
const $ = {
    "i": (id) => document.getElementById(id),
    "s": (qr) => Array.from(document.querySelectorAll(qr)),
    "c": (id) => {
        let el = document.getElementById(id);
        if (el==null) return null;
        let elClone = el.cloneNode(true);
        el.parentNode.replaceChild(elClone, el);
        return document.getElementById(id);
    },
    "v": (id) => {
        const el = document.getElementById(id);
        if (el==null) return null;
        const vl = el.value;
        const mn = el.getAttribute("min");
        const mx = el.getAttribute("max");
        if (mn!=null && vl<mn) {
            el.value = mn;
            return mn;
        }
        if (mx!=null && vl>mx) {
            el.value = mx;
            return mx;
        }
        return vl;
    }
};

const uniq = (arr) => Array.from(new Set(arr)).sort();

function monthDiff(d1, d2) {
    const to_tp = (d) => d.trim().split()[0].split("-").map(Number);
    const tp1 = to_tp(d1);
    const tp2 = to_tp(d2);
    const lng = Math.min(tp1.length, tp2.length)
    let month = (tp2[0]-tp1[0])*12;
    month -= tp1[1];
    month += tp2[1];
    if (lng == 2) {
        month += 1;
    }
    if (lng > 2) {
        const days = tp2[2] - tp1[2];
        if (days>15) month++;
    }
    return month;
}

function monthAdd(d1, m) {
    const [y, m1] = d1.split("-").map(Number);
    const y1 = (m>0?Math.floor:Math.ceil)(m/12);
    const m2 = m%12;
    const new_m = (m1+m2).toString().padStart(2, '0');
    return `${y+y1}-${new_m}`;
}

function doLoading(b) {
    if (b !== false) b = true;
    $.s(".hideInLoadding").forEach(n=>n.style.display=(b?'none':''));
}

document.addEventListener("DOMContentLoaded", function(event) {
    $.i("dbfile").addEventListener("change", function() {
        doLoading(true);
        DBLoader.getDB(this.files[0]).then((_DB)=> {
            DB.__db = _DB;
            init();
            doLoading(false);
        })
    })
});

function gRanges(subcat) {
    if (Array.isArray(subcat)) {
        if (subcat.length==0) return null;
        if (subcat.length==1) subcat=subcat[0];
    };
    const ini = $.v("ini");
    const fin = $.v("fin");
    const m = monthDiff(ini, fin);
    const where = Array.isArray(subcat)?`in (${subcat.join(', ')})`:`=${subcat}`;
    const [mn, mx, tt] = DB.one(`
    select 
        min(importe), 
        max(importe),
        sum(importe)
    from
        RESUMEN_MENSUAL
    where
        mes>='${ini}' and
        mes<='${fin}' and
        subcategoria ${where}
    `);
    return {
        "min": Math.floor(mn),
        "max": Math.ceil(mx),
        "total": Math.round(tt),
        "media": Math.round(tt/m)
    };
}

function init() {
    const ssi = DB.one("select id from subcategoria where txt='Saldo inicial'");
    const min = DB.one("select min(mes) from RESUMEN_MENSUAL");
    const max = DB.one("select max(mes) from RESUMEN_MENSUAL");
    const fin = (()=>{
        const max_date = DB.one("select max(fecha) from movimiento");
        const [max_year, max_month, max_day] = max_date.split("-");
        if (Number(max_day)>27) return `${max_year}-${max_month}`;
        return DB.one(`select max(mes) from RESUMEN_MENSUAL where mes < '${max_year}-${max_month}'`);
    })();
    const ini = DB.one(`
        select min(mes) from RESUMEN_MENSUAL where
            mes>='${monthAdd(fin, -17)}' and
            subcategoria!=${ssi}
    `);

    const $ini = $.c("ini");
    const $fin = $.c("fin");
    $ini.setAttribute("min", min);
    $ini.setAttribute("max", max);
    $fin.setAttribute("min", min);
    $fin.setAttribute("max", max);
    $ini.value = ini;
    $fin.value = fin;
    const $cat = $.s("#cat")[0];
    $.s("#cat tbody").forEach(b=>b.remove());
    const html = [];
    DB.select(`
        select id, txt from categoria
        where id!=-2
        order by txt
    `).forEach(([id, txt], index) => {
        const countcat = DB.one(`
            select 
                count(*)
            from
                RESUMEN_MENSUAL m join subcategoria s on
                    m.subcategoria=s.id
            where
                s.categoria=${id}
        `);
        if (countcat==0) return;
        const sub = DB.select(`
            select
                id,
                case
                    when txt like '%(otros)%' then 'Otros'
                    else txt
                end txt
            from subcategoria where categoria=${id}
            order by case
                when txt like '%(otros)%' then 1
                else 0
            end, txt
        `).map(([sid, stxt])=>{
            const count = DB.one("select count(*) from RESUMEN_MENSUAL where subcategoria="+sid);
            return [sid, stxt, count];
        }).filter(([sid, stxt, count]) => count>0);
        const ids = sub.map(([sid, stxt, count])=>sid);
        html.push("<tbody>")
        if (ids.length>1) {
            html.push(`
                <tr class="cat">
                    <th>
                        <input checked type="checkbox" value="${ids.join(" ")}" id="cat_${index}"/><label for="cat_${index}">${txt}</label> 
                    </th>
                </tr>
            `);
        }
        sub.forEach(([sid, stxt, count]) => {
            const tag = ids.length==1?'th':'td';
            html.push(`
                <tr class="sub">
                    <${tag}>
                        <input checked type="checkbox" value="${sid}" id="sub_${sid}"/><label for="sub_${sid}">${stxt}</label>
                    </${tag}>
                </tr>
            `);
        });
        html.push("</tbody>")
    });
    $cat.insertAdjacentHTML('beforeend', html.join("\n"));
    $.s("#cat input[id^=cat_]").forEach(n => {
        const childs = n.value.split(/\s+/).flatMap(id => $.s(`#sub_${id}`));
        const listener = () => {
            childs.forEach(x => {
                x.disabled = n.checked;
                x.checked = n.checked;
            })
        }
        n.addEventListener("change", listener);
        listener();
    });

    $.s(INPUTS).forEach(n => {
        n.addEventListener("change", doChange);
    });
    doChange();
}

function frmtNum(n, maxdec) {
    if (maxdec == null) maxdec = 0;
    const opt = {
        minimumFractionDigits: 0,
        maximumFractionDigits: maxdec,
        useGrouping: 'always'
    }
    return new Intl.NumberFormat('es-ES', opt).format(n);
}

function doChange() {
    const ko = $.s(INPUTS).filter(n=>!n.checkValidity());
    if (ko.length>0) {
        const fail = ko[0];
        setTimeout(()=>fail.reportValidity(), 100);
        return;
    }
    doLoading(true);
    const ini = $.v("ini");
    const fin = $.v("fin");
    const ids = uniq($.s("#cat input:checked").flatMap(n => {
        const val = n.value.split(/\s+/);
        return val.map(v=>Number(v));
    }));
    const thead = $.s("#cat thead tr")[0];
    if (thead.getElementsByTagName("th").length==1) thead.insertAdjacentHTML('beforeend', `
        <th>Media (€/mes)</th>
        <th>Total (€)</th>
        <th>Mínimo (€)</th>
        <th>Máximo (€)</th>
    `);
    $.s("#cat input").forEach(n => {
        const r = gRanges(n.value.split(/\s+/).map(Number));
        const tr = n.closest("tr");
        if (tr.getElementsByTagName("td").length<=2) tr.insertAdjacentHTML('beforeend', `
            <td></td>
            <td></td>
            <td></td>
            <td></td>
        `);
        const tds = Array.from(tr.querySelectorAll("th,td"));
        tds.pop().innerHTML = frmtNum(r.max);
        tds.pop().innerHTML = frmtNum(r.min);
        tds.pop().innerHTML = frmtNum(r.total);
        tds.pop().innerHTML = frmtNum(r.media);
    });
    if (ids.length==0) return;
    const select = `
        -sum(case
            when importe<0 then importe
            else 0
        end) gastos,
        sum(case
            when importe>0 then importe
            else 0
        end) ingresos
    `.trim()
    const where = `
            subcategoria in ('NaN', ${ids.join(", ")}) and
            mes>='${ini}' and 
            mes<='${fin}'
    `.trim();
    const [gst, ing] = DB.one(`
        select
            ${select}
        from
            RESUMEN_MENSUAL
        where
            ${where}
    `);

    const m = monthDiff(ini, fin);
    const y = Math.round((m / 12)*10)/10;
    const $res = $.s("#res > dl")[0];
    $res.innerHTML=`
        <dt>Tiempo</dt><dd>${m} mes${m==1?'':'es'}</dd><dd>${frmtNum(y, 1)} año${y==1?'':'s'}</dd>
        <dt>Ingreso</dt><dd>${frmtNum(ing/m)} €/mes</dd><dd>${frmtNum(ing/y)} €/año</dd>
        <dt>Gastos</dt><dd>${frmtNum(gst/m)} €/mes</dd><dd>${frmtNum(gst/y)} €/año</dd>
        <dt>Ahorro</dt><dd>${frmtNum((ing-gst)/m)} €/mes</dd><dd>${frmtNum((ing-gst)/y)} €/año</dd>
                       <dd style="grid-column: 2;">${frmtNum((1-(gst/ing))*100)} %</dd>
    `;

    const key = (()=>{
        if (m<=18) return "mes";
        const _y = "substr(mes, 1, 4)";
        const _m = "(cast(substr(mes, 6, 2) as integer) - 1)"
        const _to = (l, n) => `${_y} || '-${l}' || ((${_m} / ${n}) + 1)`;
        if (m<=(3*12)) return _to('T', 3);
        if (m<=(4*12)) return _to('C', 4);
        if (m<=(6*12)) return _to('S', 6);
        return y;
    })().trim();

    const dataset = DB.select(`
        select
            ${key},
            ${select}
        from
            RESUMEN_MENSUAL
        where
            ${where}
        group by
            ${key}
    `);

    const labels = dataset.map(i=>i[0]);
    const gastos = dataset.map(i=>Math.floor(i[1]));
    const ingres = dataset.map(i=>Math.ceil(i[2]));
    const ahorro = dataset.map(i=>Math.round(i[2]-i[1]));
    const mkDate = (obj) => {
        const color = obj.color;
        const dflt = {
            fill: true,
            pointHoverRadius: 3,
            pointRadius: 0,
            lineTension: 0.5
        }
        if (color != null) {
            delete obj['color'];
            dflt.borderColor = DFL_RGB_COLOR[color].borderColor;
            dflt.backgroundColor = DFL_RGB_COLOR[color].backgroundColor;
        }
        return Object.assign({}, dflt, obj);
    }

    const data = {
        labels: labels,
        datasets: [
            {
                label: "Gastos",
                data: gastos,
                color: "red"
            },
            {
                label: "Ingresos",
                data: ingres,
                color: "blue"
            },
            {
                label: "Ahorro",
                data: ahorro,
                color: "green",
                fill: false
            },
        ].map(mkDate)
    }
    doLoading(false);
    setChart("chart", data);
}
