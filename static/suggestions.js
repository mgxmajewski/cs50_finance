const suggestionsEndpoint = (phrase) => `http://localhost:5000/suggestions?phrase=${phrase.toUpperCase()}`
const inputDiv = document.getElementById("myInput")

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

const addSuggestionsToInput = (inputDiv) => {
    inputDiv.addEventListener("input", (e) => {
        closeAllLists(inputDiv);
            if(e.target.value !== ''){
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
    console.log(suggestionsDivWrapper)
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
                inputDiv.value = document.getElementsByTagName("input")[0].value;
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

addSuggestionsToInput(inputDiv)