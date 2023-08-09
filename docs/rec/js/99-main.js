DB = null;
const $ = {
    "i": (id) => document.getElementById(id),
    "s": (qr) => document.querySelectorAll(qr)
};

function doLoading(b) {
    if (b !== false) b = true;
    document.body.style.display=(b?'none':'');
}

function sDB(select) {
    let vals =  DB.exec(select)[0].values;
    if (vals.length>0 && vals[0].length==1) vals = vals.map(x=>x[0]);
    return vals;
}

document.addEventListener("DOMContentLoaded", function(event) {
    $.i("dbfile").addEventListener("change", function() {
        doLoading(true);
        DBLoader.getDB(this.files[0]).then((_DB)=> {
            doLoading(false);
            DB = _DB;
        })
    })
});