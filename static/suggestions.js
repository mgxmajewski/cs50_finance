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
            if(e.target.value!==''){
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
}


addSuggestionsToInput(inputDiv)


