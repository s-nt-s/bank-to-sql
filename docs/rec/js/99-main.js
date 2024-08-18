DB = null;
const $ = {
    "i": (id) => document.getElementById(id),
    "s": (qr) => Array.from(document.querySelectorAll(qr)),
    "c": (id) => {
        let el = document.getElementById(id);
        if (el==null) return null;
        let elClone = el.cloneNode(true);
        el.parentNode.replaceChild(elClone, el);
        return document.getElementById(id);
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

function doLoading(b) {
    if (b !== false) b = true;
    $.s(".hideInLoadding").forEach(n=>n.style.display=(b?'none':''));
}

function sDB(select) {
    console.debug(select);
    const r = DB.exec(select);
    let vals =  r[0].values;
    if (vals.length>0 && vals[0].length==1) vals = vals.map(x=>x[0]);
    console.debug(vals);
    return vals;
}

document.addEventListener("DOMContentLoaded", function(event) {
    $.i("dbfile").addEventListener("change", function() {
        doLoading(true);
        DBLoader.getDB(this.files[0]).then((_DB)=> {
            DB = _DB;
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
    const ini = $.i("ini").value;
    const fin = $.i("fin").value;
    const m = monthDiff(ini, fin);
    const where = Array.isArray(subcat)?`in (${subcat.join(', ')})`:`=${subcat}`;
    const [mn, mx, tt] = sDB(`
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
    `)[0];
    return {
        "min": Math.floor(mn),
        "max": Math.ceil(mx),
        "total": Math.round(tt),
        "media": Math.round(tt/m)
    };
}

function init() {
    const ini = sDB("select min(mes) from RESUMEN_MENSUAL")[0];
    const fin = sDB("select max(mes) from RESUMEN_MENSUAL")[0];
    const $ini = $.c("ini");
    const $fin = $.c("fin");
    $ini.setAttribute("min", ini);
    $ini.setAttribute("max", fin);
    $fin.setAttribute("min", ini);
    $fin.setAttribute("max", fin);
    $ini.value = ini;
    $fin.value = fin;
    const $cat = $.s("#cat")[0];
    $.s("#cat tbody").forEach(b=>b.remove());
    const html = [];
    sDB(`
        select id, txt from categoria
        where id!=-2
        order by txt
    `).forEach(([id, txt], index) => {
        const countcat = sDB(`
            select 
                count(*)
            from
                RESUMEN_MENSUAL m join subcategoria s on
                    m.subcategoria=s.id
            where
                s.categoria=${id}
        `)[0];
        if (countcat==0) return;
        const sub = sDB(`
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
            let count = sDB("select count(*) from RESUMEN_MENSUAL where subcategoria="+sid)[0];
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

    $.s("#ini, #fin, #cat input").forEach(n => {
        n.addEventListener("change", doChange);
    });
    doChange();
}

function doChange() {
    doLoading(true);
    const ini = $.i("ini").value;
    const fin = $.i("fin").value;
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
        tds.pop().innerHTML = r.max;
        tds.pop().innerHTML = r.min;
        tds.pop().innerHTML = r.total;
        tds.pop().innerHTML = r.media;
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
    const [gastos, ingreosos] = sDB(`
        select
            ${select}
        from
            RESUMEN_MENSUAL
        where
            ${where}
    `)[0];

    const m = monthDiff(ini, fin);
    const $res = $.s("#res > dl")[0];
    $res.innerHTML=`
        <dt>Meses</dt><dd>${m}</dd>
        <dt>Ingresos</dt><dd>${Math.round(ingreosos/m)} €/mes</dd>
        <dt>Gastos</dt><dd>${Math.round(gastos/m)} €/mes</dd>
        <dt>Ahorro</dt><dd>${Math.round((ingreosos-gastos)/m)} €/mes</dd>
    `;

    const dataset = sDB(`
        select
            mes,
            ${select}
        from
            RESUMEN_MENSUAL
        where
            ${where}
        group by
            mes
    `);

    const data = {
        labels: dataset.map(i=>i[0]),
        datasets: [
            {
                label: "Gastos",
                data: dataset.map(i=>Math.floor(i[1])),
                fill: true,
                borderColor: DFL_RGB_COLOR['red'].borderColor,
                backgroundColor: DFL_RGB_COLOR['red'].backgroundColor,
            },
            {
                label: "Ingresos",
                data: dataset.map(i=>Math.ceil(i[2])),
                fill: true,
                borderColor: DFL_RGB_COLOR['blue'].borderColor,
                backgroundColor: DFL_RGB_COLOR['blue'].backgroundColor,
            },
            {
                label: "Ahorro",
                data: dataset.map(i=>Math.round(i[2]-i[1])),
                fill: true,
                borderColor: DFL_RGB_COLOR['green'].borderColor,
                backgroundColor: DFL_RGB_COLOR['green'].backgroundColor,
            },
        ]
    }
    doLoading(false);
    setChart("chart", data);
}
