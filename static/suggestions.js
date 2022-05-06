// const host = `https://finance-nccixsmlaa-lm.a.run.app`
// const host = `http://34.116.183.147:5000`
const host = `http://localhost:5000`
// const host = `https://cs50finance.agilecat.io`
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

const parseSuggestions = array => {
    const result = array.map(stock => `${stock.symbol} - ${stock.company_name}`)
    return result
}

const parseSymbolForQuote = (suggestion) => {
    const result = suggestion.split(" - ")[0];
    return result
}

const addSuggestionsHandlerToInput = (inputDiv) => {
    inputDiv.addEventListener("input", (e) => {
        closeAllLists(inputDiv);
        if (e.target.value !== '') {
            fetchStocks(suggestionsEndpoint(e.target.value))
                .then(results => parseSuggestions(results))
                .then(parsedResults => addSuggestionsDivWrapper(inputDiv, parsedResults, e.target.value))
        }
    });
}

const addSuggestionsDivWrapper = (inputDiv, array, phrase) => {

    console.log(`array from addSuggestionsDivWrapper: ` + JSON.stringify(array));
    const suggestionsDivWrapper = document.createElement("DIV");
    suggestionsDivWrapper.setAttribute("id", inputDiv.id + "autocomplete-list");
    suggestionsDivWrapper.setAttribute("class", "autocomplete-items");
    inputDiv.parentNode.appendChild(suggestionsDivWrapper)
    addSuggestedStocks(inputDiv, array, phrase, suggestionsDivWrapper)
    addArrowKeySelection(inputDiv)
}

const boldMatchedPhrase = (elementToBeBolded, regexToBeBolded) => {
    elementToBeBolded.innerHTML = elementToBeBolded.innerHTML.replace(regexToBeBolded, `<strong>$&</strong>`)
}

const createRegexForPhrase = (lookupPhrase) => new RegExp(`${lookupPhrase}`, 'gi')

const addSuggestedStocks = (inputDiv, dbResultsArr, lookupPhrase, wrapper) => {
    for (let i = 0; i < dbResultsArr.length; i++) {

        /*create a DIV element for each matching element:*/
        const suggestedStockDiv = document.createElement("div");

         const regexForLookupPhrase= createRegexForPhrase(lookupPhrase)

        /*make the matching letters bold:*/
        suggestedStockDiv.innerHTML = dbResultsArr[i]
        boldMatchedPhrase(suggestedStockDiv, regexForLookupPhrase)

        /*insert a input field that will hold the current array item's value:*/
        suggestedStockDiv.innerHTML += "<input type='hidden' value='" + dbResultsArr[i] + "'>";

        /*execute a function when someone clicks on the item value (DIV element):*/
        suggestedStockDiv.addEventListener("click", function (e) {

            /*insert the value for the autocomplete text field:*/
            inputDiv.value = e.target.getElementsByTagName("input")[0].value;

            /*close the list of autocompleted values,
            (or any other open lists of autocompleted values:*/
            closeAllLists(inputDiv);
        });
        wrapper.appendChild(suggestedStockDiv);
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

requestStockForm.addEventListener('submit', function (event) {
    event.preventDefault();
    console.log(`poop ${inputDiv.value}`)
    inputDiv.value = parseSymbolForQuote(inputDiv.value);
    inputDiv.setAttribute('style', 'background-color: grey');
    requestStockForm.submit()
});

addSuggestionsHandlerToInput(inputDiv)