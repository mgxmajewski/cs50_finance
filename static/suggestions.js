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

const logFetchedStocks = results => console.log(results)

inputDiv.addEventListener("keyup", (e) => {
    e.preventDefault()
    if(e.target.value !== ''){
        fetchStocks(suggestionsEndpoint(e.target.value))
            .then(results => parseSuggestions(results))
            .then(parsedSuggestions => logFetchedStocks(parsedSuggestions))
    }
});


const FetchedStocks = results => console.log(results)