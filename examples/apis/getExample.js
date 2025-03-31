const coinsUrl = "https://www.random.org/integers/?format=plain&num=18&min=2&max=3&col=18&base=10";
const stalksUrl = "https://www.random.org/decimal-fractions/?num=18&dec=2&col=18&format=plain&rnd=new";


function doThrow() {
    let method = document.getElementById("method").value;
    let resultSpan = document.getElementById("result");
    let url;
    if (method == "coins") {
        url = coinsUrl;
    } else {
        url = stalksUrl;
    }
    fetch(url).then(response => {
        // this returns a Promise(), not a string
        return response.text();
    }).then(result => {
        resultSpan.innerText = result;
    }).catch(error => {
        console.log(error);
    });
};
