class DBLoader {
    static SQL = null;
    static init() {
        // https://gist.github.com/SMUsamaShah/358fba159cb41fe469fc61e7db444c0e
        const wasm_strbuffer = atob(SQLBASE64);
        let wasm_codearray = new Uint8Array(wasm_strbuffer.length);
        for (var i in wasm_strbuffer) wasm_codearray[i] = wasm_strbuffer.charCodeAt(i);
    
        return initSqlJs({
            locateFile: (filename) => URL.createObjectURL(
                new Blob([wasm_codearray], {type: 'application/wasm'})
            )
        }).then((_SQL) => {
            DBLoader.SQL = _SQL;
        })
    }
    static readFile(file) {
        return new Promise((resolve, reject) => {
            const r = new FileReader();  
            r.onload = () => {
                resolve(r.result)
            };
            r.onerror = reject;
            r.readAsArrayBuffer(file);
        });
    }
    static getDB(file) {
        if (DBLoader.SQL == null) return DBLoader.init().then(() => {
            return DBLoader.getDB(file);
        })
        return DBLoader.readFile(file).then((result) => {
            const Uints = new Uint8Array(result);
            return new DBLoader.SQL.Database(Uints);
        })
    }
}

class DB {
    static __db = null;
    static __exec(sql) {
        return DB.__db.exec(sql);
    }
    static __select(sql) {
        const r = DB.__exec(sql);
        return r[0].values;
    }
    static __one(sql) {
        let vals = DB.__select(sql);
        if (vals.length == 0) return null;
        const one = vals[0];
        if (one.length == 0) return null;
        const val = one.length==1 ? one[0] : one;
        return val;
    }
    static select(sql) {
        console.debug(sql);
        let vals = DB.__select(sql);
        if (vals.length>0 && vals[0].length==1) vals = vals.map(x=>x[0]);
        console.debug(vals);
        return vals;
    }
    static one(sql) {
        console.debug(sql);
        const val = DB.__one(sql);
        console.debug(val);
        return val;
    }
}