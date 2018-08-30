
// cat models

var model = {
    currentCat: null,
    cats: [
        {
            clickCount: 0,
            name: 'High Five',
            imgSrc: 'img/patinha.jpg',
        },
        {
            clickCount: 0,
            name: 'Tomilho',
            imgSrc: 'img/tomilho.jpg',
        },
        {
            clickCount: 0,
            name: 'Canjica',
            imgSrc: 'img/canjica.jpg',
        },
        {
            clickCount: 0,
            name: 'Quinoa',
            imgSrc: 'img/quinoa.jpg',
        },
    ],
};


// Octopus

var octopus = {

    init: function () {
        // set our current cat to the first one in the list
        model.currentCat = model.cats[0];

        // tell our views to initialize
        catListView.init();
        catView.init();
        formView.init();
    },

    getCurrentCat: function () {
        return model.currentCat;
    },

    getCats: function () {
        return model.cats;
    },

    updateCat: function (name, img, clicks) {
        var cat = this.getCurrentCat();
        cat.name = name;
        cat.imgSrc = img;
        cat.clickCount = clicks;
    },

    // set the currently-selected cat to the object passed in
    setCurrentCat: function (cat) {
        model.currentCat = cat;
    },

    // increments the counter for the currently-selected cat
    incrementCounter: function () {
        model.currentCat.clickCount++;
        catView.render();
    }
};


// View

var catView = {

    init: function () {
        // store pointers to our DOM elements for easy access later
        this.catElem = document.getElementById('cat');
        this.catNameElem = document.getElementById('cat-name');
        this.catImageElem = document.getElementById('cat-img');
        this.countElem = document.getElementById('cat-count');

        // on click, increment the current cat's counter
        this.catImageElem.addEventListener('click', function () {
            octopus.incrementCounter();
            formView.populateForm();
        });

        // render this view (update the DOM elements with the right values)
        this.render();
    },

    render: function () {
        // update the DOM elements with values from the current cat
        var currentCat = octopus.getCurrentCat();
        this.countElem.textContent = currentCat.clickCount;
        this.catNameElem.textContent = currentCat.name;
        this.catImageElem.src = currentCat.imgSrc;
    }
};

var catListView = {

    init: function () {
        // store the DOM element for easy access later
        this.catListElem = document.getElementById('cat-list');

        // render this view (update the DOM elements with the right values)
        this.render();
    },

    render: function () {
        var cat, elem, i;
        // get the cats we'll be rendering from the octopus
        var cats = octopus.getCats();

        // empty the cat list
        this.catListElem.innerHTML = '';

        // loop over the cats
        for (i = 0; i < cats.length; i++) {
            // this is the cat we're currently looping over
            cat = cats[i];

            // make a new cat list item and set its text
            elem = document.createElement('li');
            elem.textContent = cat.name;

            // on click, setCurrentCat and render the catView
            // (this uses our closure-in-a-loop trick to connect the value
            //  of the cat variable to the click event function)
            elem.addEventListener('click', (function (catCopy) {
                return function () {
                    octopus.setCurrentCat(catCopy);
                    catView.render();
                    formView.populateForm();
                };
            })(cat));

            // finally, add the element to the list
            this.catListElem.appendChild(elem);
        }
    }
};

var formView = {

    init: function () {
        this.form = document.getElementById('admin-form');
        this.form.style.display = "none";

        this.render();
    },

    render: function () {
        var adminbutton = document.getElementById('admin-btn');
        adminbutton.addEventListener('click', function () {
            formView.toggleForm();
        });

        var cancelbutton = document.getElementById('cancel-btn');
        cancelbutton.addEventListener('click', function () {
            formView.toggleForm();
        });

        var savebutton = document.getElementById('save-btn');
        savebutton.addEventListener('click', function () {
            nameInput = document.getElementById('name').value;
            imgInput = document.getElementById('imgurl').value;
            clickInput = document.getElementById('clicks').value;

            octopus.updateCat(nameInput, imgInput, clickInput);
            catView.render();
            catListView.render();
            formView.toggleForm();
        });

    },

    toggleForm: function () {
        if (this.form.style.display === "none") {
            this.form.style.display = "block";
            this.populateForm();
        } else {
            this.form.style.display = "none";
        }
    },

    populateForm: function () {
        cat = octopus.getCurrentCat();
        document.getElementById('name').value = cat.name;
        document.getElementById('imgurl').value = cat.imgSrc;
        document.getElementById('clicks').value = cat.clickCount;
    }

};




// make it go!
octopus.init();