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