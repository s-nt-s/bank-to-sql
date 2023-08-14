DB = null;
const $ = {
    "i": (id) => document.getElementById(id),
    "s": (qr) => document.querySelectorAll(qr),
    "c": (id) => {
        let el = document.getElementById(id);
        if (el==null) return null;
        let elClone = el.cloneNode(true);
        el.parentNode.replaceChild(elClone, el);
        return document.getElementById(id);
    }
};

function doLoading(b) {
    if (b !== false) b = true;
    document.body.style.display=(b?'none':'');
}

function sDB(select) {
    const r = DB.exec(select);
    let vals =  r[0].values;
    if (vals.length>0 && vals[0].length==1) vals = vals.map(x=>x[0]);
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
                    <input type="checkbox" value="${ids.join(" ")}" id="cat_${index}"/>
                    <label for="cat_${index}">${txt}</label> 
            `);
            html.push(`<ul>`);
        }
        sub.forEach(([sid, stxt, count]) => {
            html.push(`
            <li>
                <code>${count}</code>
                <input type="checkbox" value="${sid}" id="sub_${sid}"/>
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
        n.parentNode.addEventListener("change", (e=> {
            e.target.parentNode.querySelectorAll("ul li input").forEach(x => {
                x.disabled = n.checked;
            })
        }));
    });

    $.s("#ini, #fin, #cat input").forEach(n => {
        n.addEventListener("change", doChange);
    });
}

function doChange() {
    const ini = $.i("ini").value;
    const fin = $.i("fin").value;
    const ids = [... new Set(Array.from($.s("#cat input:checked")).flatMap(n => {
        const val = n.value.split(/\s+/);
        return val.map(v=>Number(v));
    }))].sort();
    console.log(ids);
}