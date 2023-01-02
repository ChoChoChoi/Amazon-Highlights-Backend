// YouTube DATA API v3
// https://developers.google.com/youtube/v3/docs/

var request = require('request');

// search 예제
var optionParams={
    part:"snippet",
    key:"AIzaSyAvZuCRcx7sWA-OUiPjkml_Xv3F4aNXGEc",
    channelId:"UCdoadna9HFHsxXWhafhNvKw",
    type:"video",
    order:"date",
    maxResult:10
}

//한글 검색 시 url encoding 필요
// optionParams.q=encodeURI(optionParams.q);

var url="https://www.googleapis.com/youtube/v3/search?";
for(var option in optionParams){
    url+=option+"="+optionParams[option]+"&";
}

// url의 마지막에 붙은 & 문자 삭제
url=url.substr(0, url.length-1);

request(url, function(err, res, body){
	//console.log(body)
	
	//json형식을 서버로 부터 받음
	var data=JSON.parse(body).items;

    var videoUrl = "https://youtube.com/watch?";
	for(var content in data){
		
		//youtube downloader에 videoId 넘기면 됨.
		console.log("title "+data[content].snippet.title+", videoId: "+data[content].id.videoId+", publishedAt: "+data[content].snippet.publishedAt);

	}
});