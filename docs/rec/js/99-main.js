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
    if (d1==null || d2==null) return null;
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

class BankManager {
    constructor() {
        this.ini = null;
        this.fin = null;
        this.meses = null;
        this.subs = [];
        this.load();
    }
    load() {
        this.ini = $.v("ini");
        this.fin = $.v("fin");
        this.meses = monthDiff(this.ini, this.fin);
        this.subs = uniq($.s("#cat input:checked").flatMap(n => {
            const val = n.value.split(/\s+/);
            return val.map(v=>Number(v));
        }))
    }
    get __select() {
        return `
            -sum(case
                when importe<0 then importe
                else 0
            end) gastos,
            sum(case
                when importe>0 then importe
                else 0
            end) ingresos
        `.trim()
    }
    get __where() {
        if (this.subs == null || this.length==0) return "1!=1"
        const wSub = this.subs.length==1?`= ${this.subs[0]}`:`in (${this.subs.join(", ")})`;
        return `
            subcategoria ${wSub} and
            mes>='${this.ini}' and 
            mes<='${this.fin}'
        `.trim();
    }
    get __key() {
        if (this.meses<=18) return "mes";
        const _y = "substr(mes, 1, 4)";
        const _m = "(cast(substr(mes, 6, 2) as integer) - 1)"
        const _to = (l, n) => `${_y} || '-${l}' || ((${_m} / ${n}) + 1)`;
        if (this.meses<=(3*12)) return _to('T', 3);
        if (this.meses<=(4*12)) return _to('C', 4);
        if (this.meses<=(6*12)) return _to('S', 6);
        return _y;
    }
    getDataset() {
        return DB.select(`
            select
                ${this.__key},
                ${this.__select}
            from
                RESUMEN_MENSUAL
            where
                ${this.__where}
            group by
                ${this.__key}
        `);
    }
    getResumen() {
        const [gst, ing] = DB.one(`
            select
                ${this.__select}
            from
                RESUMEN_MENSUAL
            where
                ${this.__where}
        `);
        return {
            "ingresos": ing,
            "gastos": gst,
            "ahorro": ing-gst
        }
    }
    getMovimientos(key) {
        let sql = `
        with R as (
            select
                ${this.__key} k,
                subcategoria,
                concepto,
                sum(importe) importe
            from
                RESUMEN_MENSUAL
            where
                ${this.__where},
                subcategoria,
                concepto
            group by
                ${this.__key}
        )
        select * from R
        `.trim()
        if (key != null) sql += ` where k='${key}'`;
        return DB.select(sql);
    }
    getRange(subcat) {
        if (Array.isArray(subcat)) {
            if (subcat.length==0) return null;
            if (subcat.length==1) subcat=subcat[0];
        };
        const where = Array.isArray(subcat)?`in (${subcat.join(', ')})`:`=${subcat}`;
        const [mn, mx, tt] = DB.one(`
        select 
            min(importe), 
            max(importe),
            sum(importe)
        from
            RESUMEN_MENSUAL
        where
            mes>='${this.ini}' and
            mes<='${this.fin}' and
            subcategoria ${where}
        `);
        return {
            "min": Math.floor(mn),
            "max": Math.ceil(mx),
            "total": Math.round(tt),
            "media": Math.round(tt/this.meses)
        };
    }
    getCatSubCat() {
        const rtn = [];
        DB.select(`
            select id, txt from categoria
            where id!=-2
            order by txt
        `).forEach(([id, txt]) => {
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
            rtn.push([
                {id: id, txt:txt},
                sub.map(([sid, stxt, count])=>{return {id:sid, txt:stxt}})
            ]);
        });
        return rtn;
    }
}

BANK = new BankManager();

function doLoading(b) {
    const hideInLoadding = ".hideInLoadding";
    const hideInImport = ".hideInImport";
    const hideIn = hideInLoadding+", "+hideInImport;
    if (DB.__db == null) {
        $.s(hideIn).forEach(n=>n.style.display='none');
        return;
    }
    $.s(hideInImport).forEach(n=>n.style.display='');
    if (b !== false) b = true;
    $.s(hideInLoadding).forEach(n=>n.style.display=(b?'none':''));
}

document.addEventListener("DOMContentLoaded", function(event) {
    $.i("dbfile").addEventListener("change", function() {
        DB.__db = null;
        doLoading(true);
        DBLoader.getDB(this.files[0]).then((_DB)=> {
            DB.__db = _DB;
            init();
            doLoading(false);
        })
    })
});


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

    BANK.load();

    const $cat = $.s("#cat")[0];
    $.s("#cat tbody").forEach(b=>b.remove());
    const html = [];
    BANK.getCatSubCat().forEach(([cat, subs]) => {
        html.push("<tbody>")
        if (subs.length>1) {
            html.push(`
                <tr class="cat">
                    <th>
                        <input checked type="checkbox" value="${subs.map(s=>s.id).join(' ')}" id="cat_${cat.id}"/><label for="cat_${cat.id}">${cat.txt}</label> 
                    </th>
                </tr>
            `);
        }
        subs.forEach((sub) => {
            const tag = subs.length==1?'th':'td';
            html.push(`
                <tr class="sub">
                    <${tag}>
                        <input checked type="checkbox" value="${sub.id}" id="sub_${sub.id}"/><label for="sub_${sub.id}">${sub.txt}</label>
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
    BANK.load();

    const thead = $.s("#cat thead tr")[0];
    if (thead.getElementsByTagName("th").length==1) thead.insertAdjacentHTML('beforeend', `
        <th>Media<br/>(€/mes)</th>
        <th>Total<br/>(€)</th>
        <th>Mínimo<br/>(€)</th>
        <th>Máximo<br/>(€)</th>
    `);
    $.s("#cat input").forEach(n => {
        const r = BANK.getRange(n.value.split(/\s+/).map(Number));
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
    if (BANK.subs.length==0) return;
    
    const rsm = BANK.getResumen();

    const y = Math.round((BANK.meses / 12)*10)/10;
    const $res = $.s("#res > dl")[0];
    $res.innerHTML=`
        <dt>Tiempo</dt><dd>${BANK.meses} mes${BANK.meses==1?'':'es'}</dd><dd>${frmtNum(y, 1)} año${y==1?'':'s'}</dd>
        <dt>Ingreso</dt><dd>${frmtNum(rsm.ingresos/BANK.meses)} €/mes</dd><dd>${frmtNum(rsm.ingresos/y)} €/año</dd>
        <dt>Gastos</dt><dd>${frmtNum(rsm.gastos/BANK.meses)} €/mes</dd><dd>${frmtNum(rsm.gastos/y)} €/año</dd>
        <dt>Ahorro</dt><dd>${frmtNum(rsm.ahorro/BANK.meses)} €/mes</dd><dd>${frmtNum(rsm.ahorro/y)} €/año</dd>
                       <dd style="grid-column: 2;">${frmtNum((1-(rsm.gastos/rsm.ingresos))*100)} %</dd>
    `;

    const dataset = BANK.getDataset();

    const labels = dataset.map(i=>i[0]);
    const ingres = dataset.map(i=>Math.ceil(i[2]));
    const gastos = dataset.map(i=>Math.floor(i[1]));
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
                label: "Ingresos",
                data: ingres,
                color: "blue"
            },
            {
                label: "Gastos",
                data: gastos,
                color: "red"
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
    setLineChart(
        "chart",
        data,
        (e, elements) => {
            if (elements.length==0) return;
            const element = elements[0];
            const index = element.index;
            const x = e.chart.data.labels[index];
            if (!/^\d{4}-\d{2}$/.test(x)) return;
            const y = elements.map(elm=>e.chart.data.datasets[elm.datasetIndex].label);
            console.log(x, y);
        }
    );
}
