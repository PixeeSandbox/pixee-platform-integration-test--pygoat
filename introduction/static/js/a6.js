event5 = function(){
    const code = document.getElementById('a6_t1').value;
    const myHeaders = new Headers();
    const formdata = new FormData();

    formdata.append("code", code);
    const requestOptions = {
        method: 'POST',
        headers: myHeaders,
        body: formdata,
        redirect: 'follow'
    };
    fetch("/2021/discussion/A6/api2", requestOptions)
    .then(response => response.text())
    .then(result => {
        let data = JSON.parse(result);
        if (data.message == "success"){
            alert("code saved");
        }  // parse JSON string into object
    })
    .catch(error => console.log('error', error));
}

event6 = function(){
    const code = document.getElementById('a6_t1').value;
    const myHeaders = new Headers();
    const formdata = new FormData();

    formdata.append("code", code);
    const requestOptions = {
        method: 'POST',
        headers: myHeaders,
        body: formdata,
        redirect: 'follow'
    };
    fetch("/2021/discussion/A6/api", requestOptions)
    .then(response => response.text())
    .then(result => {
        let data = JSON.parse(result);  // parse JSON string into object
        console.log(data.vulns);
        document.getElementById("a6_d5").style.display = 'flex';
        // document.getElementById("a6_d5").innerText =  data.vulns;

        for (let i = 0; i < data.vulns.length; i++) {
            const vuln = data.vulns[i];
            const vuln_div = document.createElement("div");
            vuln_div.innerText = JSON.stringify(vuln)   ;
            document.getElementById("a6_d5").appendChild(vuln_div);
        }
        
    })
    .catch(error => console.log('error', error));
}

