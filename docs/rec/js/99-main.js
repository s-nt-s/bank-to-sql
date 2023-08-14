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
    if (typeof d1 === "string") d1 = new Date(d1);
    if (typeof d2 === "string") d2 = new Date(d2);
    let month = (d2.getFullYear() - d1.getFullYear())*12;
    month -= d1.getMonth();
    month += d2.getMonth();
    let days = d2.getDate() - d1.getDate();
    if (days>15) month++;
    return month;
}

function doLoading(b) {
    if (b !== false) b = true;
    document.body.style.display=(b?'none':'');
}

function sDB(select) {
    console.log(select);
    const r = DB.exec(select);
    let vals =  r[0].values;
    if (vals.length>0 && vals[0].length==1) vals = vals.map(x=>x[0]);
    console.log(vals);
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

function init() {
    const ini = sDB("select min(fecha) from MOV")[0];
    const fin = sDB("select max(fecha) from MOV")[0];
    const $ini = $.c("ini");
    const $fin = $.c("fin");
    $ini.setAttribute("min", ini);
    $ini.setAttribute("max", fin);
    $fin.setAttribute("min", ini);
    $fin.setAttribute("max", fin);
    $ini.value = ini;
    $fin.value = fin;
    const $cat = $.s("#cat > ul")[0];
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
                movimiento m join subcategoria s on
                    m.subcategoria=s.id
            where
                s.categoria=${id}
        `)[0];
        if (countcat==0) return;
        const sub = sDB(`
            select id, txt from subcategoria where categoria=${id}
            order by txt
        `).map(([sid, stxt])=>{
            let count = sDB("select count(*) from movimiento where subcategoria="+sid)[0];
            return [sid, stxt, count];
        }).filter(([sid, stxt, count]) => count>0);
        const ids = sub.map(([sid, stxt, count])=>sid);
        if (ids.length>1) {
            html.push(`
                <li>
                    <code>${countcat}</code>
                    <input checked type="checkbox" value="${ids.join(" ")}" id="cat_${index}"/>
                    <label for="cat_${index}">${txt}</label> 
            `);
            html.push(`<ul>`);
        }
        sub.forEach(([sid, stxt, count]) => {
            html.push(`
            <li>
                <code>${count}</code>
                <input checked type="checkbox" value="${sid}" id="sub_${sid}"/>
                <label for="sub_${sid}">${stxt}</label> 
            </li>
            `);
        });

        if (ids.length>1) {
            html.push(`</ul>`);
            html.push(`</li>`);
        }
    });
    $cat.innerHTML = html.join("\n");
    $.s("#cat input").forEach(n => {
        if (n.parentNode.getElementsByTagName("li").length==0) return;
        const childs = n.value.split(/\s+/).flatMap(id => $.s(`#cat input[value='${id}']`));
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
    const ini = $.i("ini").value;
    const fin = $.i("fin").value;
    const ids = uniq($.s("#cat input:checked").flatMap(n => {
        const val = n.value.split(/\s+/);
        return val.map(v=>Number(v));
    }));
    if (ids.length==0) return;
    const [gastos, ingreosos] = sDB(`
        select
            -sum(case
                when importe<0 then importe
                else 0
            end) gastos,
            sum(case
                when importe>0 then importe
                else 0
            end) ingresos
        from
            movimiento
        where
            subcategoria in ('NaN', ${ids.join(", ")}) and
            fecha>='${ini}' and 
            fecha<='${fin}'
    `)[0];

    const m = monthDiff(ini, fin);
    const $res = $.s("#res > ul")[0];
    $res.innerHTML=`
        <li><strong>Meses</strong>: ${m}</li>
        <li><strong>Ingresos</strong>: ${Math.round(ingreosos/m)} €/mes</li>
        <li><strong>Gastos</strong>: ${Math.round(gastos/m)} €/mes</li>
        <li><strong>Ahorro</strong>: ${Math.round((ingreosos-gastos)/m)} €/mes</li>
    `;
}