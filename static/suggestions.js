const suggestionsEndpoint = (phrase) => `http://localhost:5000/suggestions?phrase=${phrase.toUpperCase()}`

// Handle fetch request
async function fetchStocks(url) {
    try {
        const response = await fetch(url);
        return await response.json();
    } catch (error) {
        throw error;
    }
}

fetchStocks(suggestionsEndpoint('app')).then(results => FetchedStocks(results))

const FetchedStocks = results => console.log(results)