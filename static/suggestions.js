const host = `https://finance-nccixsmlaa-lm.a.run.app`
// const host = `http://127.0.0.1:5000`
const suggestionsEndpoint = (phrase) => `${host}/suggestions?phrase=${phrase.toUpperCase()}`
const inputDiv = document.getElementById("myInput")
const requestStockForm = document.getElementById("stock form")

// Handle fetch request
async function fetchStocks(url) {
    try {
        const response = await fetch(url);
        return await response.json();
    } catch (error) {
        throw error;
    }
}

const parseSuggestions = array => array.map(stock => `${stock.symbol} - ${stock.company_name}`)

const parseSymbolForQuote = (suggestion) => suggestion.split(" - ")[0];

const addSuggestionsHandlerToInput = (inputDiv) => {
    inputDiv.addEventListener("input", (e) => {
        closeAllLists(inputDiv);
        if (e.target.value !== '') {
            fetchStocks(suggestionsEndpoint(e.target.value))
                .then(results => parseSuggestions(results))
                .then(parsedResults => addSuggestionsDivWrapper(inputDiv, parsedResults))
        }
    });
}

const addSuggestionsDivWrapper = (inputDiv, array) => {

    const suggestionsDivWrapper = document.createElement("DIV");
    suggestionsDivWrapper.setAttribute("id", inputDiv.id + "autocomplete-list");
    suggestionsDivWrapper.setAttribute("class", "autocomplete-items");
    inputDiv.parentNode.appendChild(suggestionsDivWrapper)
    addSuggestedStocks(inputDiv, array, suggestionsDivWrapper)
    addArrowKeySelection(inputDiv)
}

const addSuggestedStocks = (inputDiv, arr, wrapper) => {
    for (let i = 0; i < arr.length; i++) {
        if (arr[i].substr(0, inputDiv.value.length).toUpperCase() === inputDiv.value.toUpperCase()) {
            /*create a DIV element for each matching element:*/
            const suggestedStock = document.createElement("DIV");
            /*make the matching letters bold:*/
            suggestedStock.innerHTML = "<strong>" + arr[i].substr(0, inputDiv.value.length) + "</strong>";
            suggestedStock.innerHTML += arr[i].substr(inputDiv.value.length);
            /*insert a input field that will hold the current array item's value:*/
            suggestedStock.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
            /*execute a function when someone clicks on the item value (DIV element):*/
            suggestedStock.addEventListener("click", function (e) {
                /*insert the value for the autocomplete text field:*/
                console.log(parseSymbolForQuote(e.target.getElementsByTagName("input")[0].value))
                inputDiv.value = e.target.getElementsByTagName("input")[0].value;

                /*close the list of autocompleted values,
                (or any other open lists of autocompleted values:*/
                closeAllLists(inputDiv);
            });
            wrapper.appendChild(suggestedStock);
        }
    }
}

const closeAllLists = (inputDiv, elementToKeep) => {
    /*close all autocomplete lists in the document,
    except the one passed as an argument:*/
    const autocompleteList = document.getElementsByClassName('autocomplete-items');
    for (let i = 0; i < autocompleteList.length; i++) {
        if (elementToKeep !== autocompleteList[i] && elementToKeep !== inputDiv) {
            autocompleteList[i].parentNode.removeChild(autocompleteList[i]);
        }
    }
}

const addArrowKeySelection = (inputDiv) => {

    let currentFocus = -1;
    inputDiv.addEventListener("keydown", function (e) {
        let x = document.getElementById(inputDiv.id + 'autocomplete-list');
        if (x) x = x.getElementsByTagName('div');
        if (e.keyCode === 40) {
            /*If the arrow DOWN key is pressed,
            increase the currentFocus variable:*/
            currentFocus++;
            /*and and make the current item more visible:*/
            addActive(x);
        } else if (e.keyCode === 38) { //up
            /*If the arrow UP key is pressed,
            decrease the currentFocus variable:*/
            currentFocus--;
            /*and and make the current item more visible:*/
            addActive(x);
        } else if (e.keyCode === 13) {
            /*If the ENTER key is pressed, prevent the form from being submitted,*/
            e.preventDefault();
            if (currentFocus > -1) {
                /*and simulate a click on the "active" item:*/
                if (x) x[currentFocus].click();
            }
        }
    });

    function addActive(x) {
        /*a function to classify an item as "active":*/
        if (!x) return false;
        /*start by removing the "active" class on all items:*/
        removeActive(x);
        if (currentFocus >= x.length) {
            currentFocus = 0;
        }
        if (currentFocus < 0) {
            currentFocus = (x.length - 1);
        }
        /*add class "autocomplete-active":*/
        x[currentFocus].classList.add("autocomplete-active");
    }

    function removeActive(x) {
        /*a function to remove the "active" class from all autocomplete items:*/
        for (let i = 0; i < x.length; i++) {
            x[i].classList.remove("autocomplete-active");
        }
    }
}


document.addEventListener("click", function (e) {
    closeAllLists(e.target);
});
requestStockForm.addEventListener('submit', function(event){
    event.preventDefault();
    console.log(`poop ${inputDiv.value}`)
    inputDiv.value = parseSymbolForQuote(inputDiv.value);
    inputDiv.setAttribute('style', 'background-color: grey');
    requestStockForm.submit()
});

addSuggestionsHandlerToInput(inputDiv)