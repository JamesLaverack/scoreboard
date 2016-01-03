var players_bloodhound = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: {
	url: '/api/v1/player',
	cache: false
    }
});

$('.player-list').typeahead({
    name: 'players',
    source: players_bloodhound.ttAdapter()
});
