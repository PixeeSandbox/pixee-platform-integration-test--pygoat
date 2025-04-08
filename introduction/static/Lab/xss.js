const coll = document.getElementsByClassName("coll");
const coll2 = document.getElementsByClassName("coll2");
let i;

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    this.classList.toggle("active");
    let content = this.nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
}
for (i = 0; i < coll2.length; i++) {
  coll2[i].addEventListener("click", function() {
    this.classList.toggle("active");
    let content = this.nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
}
function SendToServer(){

        comment=document.getElementById("comment").value;


        let xhr;
        xhr = new XMLHttpRequest();
        xml="<?xml version='1.0'?>"+"<comm>"+"<text>"+comment+"</text>"+"</comm>";
        const url = $("#Url").attr("data-url");
       xhr.open("POST", url, true);
       xhr.setRequestHeader("Content-Type", "text/xml");
       xhr.send(xml);

}
