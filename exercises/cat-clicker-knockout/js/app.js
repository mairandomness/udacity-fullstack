var initialCats = [
  {
    clickCount: 0,
    name: "Tabby",
    imgSrc: "img/434164568_fea0ad4013_z.jpg",
    imgAttribution: "https://www.flickr.com/photos/bigtallguy/434164568",
    nicknames: ["Cutie", "Lovely Demon", "Lord of Destruction"]
  },
  {
    clickCount: 0,
    name: "Tiger",
    imgSrc: "img/4154543904_6e2428c421_z.jpg",
    imgAttribution: "https://www.flickr.com/photos/xshamx/4154543904",
    nicknames: ["Tigerling"]
  },
  {
    clickCount: 0,
    name: "Scaredy",
    imgSrc: "img/22252709_010df3379e_z.jpg",
    imgAttribution: "https://www.flickr.com/photos/kpjas/22252709",
    nicknames: ["Shaky"]
  },
  {
    clickCount: 0,
    name: "Shadow",
    imgSrc: "img/1413379559_412a540d29_z.jpg",
    imgAttribution: "https://www.flickr.com/photos/malfet/1413379559",
    nicknames: ["Darkz0r"]
  },
  {
    clickCount: 0,
    name: "Sleepy",
    imgSrc: "img/9648464288_2516b35537_z.jpg",
    imgAttribution: "https://www.flickr.com/photos/onesharp/9648464288",
    nicknames: ["lazy fuck"]
  }
];

var Cat = function(data) {
  var self = this;
  this.clickCount = ko.observable(data.clickCount);
  this.name = ko.observable(data.name);
  this.imgSrc = ko.observable(data.imgSrc);
  this.imgAttribution = ko.observable(data.imgAttribution);
  this.nicknames = ko.observableArray(data.nicknames);

  this.catLevel = ko.computed(function() {
    var clicks = self.clickCount();
    if (clicks < 10) {
      return "Newborn";
    } else if (clicks < 100) {
      return "Infant";
    } else if (clicks < 200) {
      return "Teen";
    } else if (clicks < 500) {
      return "Adult";
    } else {
      return "Ninja";
    }
  });
};

var ViewModel = function() {
  var self = this;

  this.catList = ko.observableArray([]);

  initialCats.forEach(function(catItem) {
    self.catList.push(new Cat(catItem));
  });

  this.currentCat = ko.observable(this.catList()[0]);

  this.incrementCounter = function() {
    self.currentCat().clickCount(self.currentCat().clickCount() + 1);
  };
};

ko.applyBindings(new ViewModel());

this.nicknames = ko.observableArray([
  "Cutie",
  "Lovely Demon",
  "Lord of Destruction"
]);
