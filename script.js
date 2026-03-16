let moviesData = []

fetch("database.json")
.then(res => res.json())
.then(data => {

moviesData = data

loadCategories(data)

})

function loadCategories(data){

let categories = [...new Set(data.map(m=>m.category))]

let catDiv = document.getElementById("categories")

categories.forEach(cat=>{

let btn = document.createElement("button")

btn.innerText = cat

btn.onclick = ()=>showMovies(cat)

catDiv.appendChild(btn)

})

}

function showMovies(category){

let movies = moviesData.filter(m=>m.category === category)

let container = document.getElementById("movies")

container.innerHTML=""

movies.forEach(movie=>{

let linksHTML = ""

movie.downloads.forEach(link=>{

let quality = "HD"

if(link.includes("480")) quality="480p"
if(link.includes("720")) quality="720p"
if(link.includes("1080")) quality="1080p"

linksHTML += `
<div class="quality">
${quality}

<button onclick="playVideo('${link}')">▶</button>
<button onclick="window.open('${link}')">⬇</button>
<button onclick="copyLink('${link}')">📋</button>

</div>
`

})

let card = document.createElement("div")

card.className="card"

card.innerHTML = `

<img src="${movie.poster}">

<h3>${movie.name}</h3>

${linksHTML}

`

container.appendChild(card)

})

}

function copyLink(link){

navigator.clipboard.writeText(link)

alert("Link Copied!")

}
function playVideo(link){

let player = document.getElementById("videoPlayer")

player.src = link

document.getElementById("playerModal").style.display="flex"

}

function closePlayer(){

let player = document.getElementById("videoPlayer")

player.pause()

document.getElementById("playerModal").style.display="none"

}