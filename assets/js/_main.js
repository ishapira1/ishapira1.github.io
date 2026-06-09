/* ==========================================================================
   jQuery plugin settings and other scripts
   ========================================================================== */

$(document).ready(function(){
  var THEME_STORAGE_KEY = "theme-preference";
  var LIGHT_THEME_COLOR = "#f5f7fb";
  var DARK_THEME_COLOR = "#272935";
  var root = document.documentElement;
  var darkModeQuery = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;
  var $themeToggle = $("#theme-toggle");
  var $themeToggleText = $themeToggle.find(".theme-toggle__text");
  var themeColorMeta = document.querySelector('meta[name="theme-color"]');

  var isExplicitTheme = function(theme) {
    return theme === "light" || theme === "dark";
  };

  var getEffectiveTheme = function() {
    var explicitTheme = root.getAttribute("data-theme");

    if (isExplicitTheme(explicitTheme)) {
      return explicitTheme;
    }

    return darkModeQuery && darkModeQuery.matches ? "dark" : "light";
  };

  var syncThemeColor = function(theme) {
    if (themeColorMeta) {
      themeColorMeta.setAttribute("content", theme === "dark" ? DARK_THEME_COLOR : LIGHT_THEME_COLOR);
    }
  };

  var syncThemeToggle = function() {
    if ($themeToggle.length === 0) {
      return;
    }

    var theme = getEffectiveTheme();
    var nextTheme = theme === "dark" ? "light" : "dark";
    var label = nextTheme === "dark" ? "Activate dark mode" : "Activate light mode";

    $themeToggle.attr("aria-pressed", theme === "dark" ? "true" : "false");
    $themeToggle.attr("aria-label", label);
    $themeToggle.attr("title", label);
    $themeToggleText.text(label);
  };

  var setThemePreference = function(theme) {
    root.setAttribute("data-theme", theme);

    try {
      window.localStorage.setItem(THEME_STORAGE_KEY, theme);
    } catch (error) {}

    syncThemeColor(theme);
    syncThemeToggle();
  };

  $themeToggle.on("click", function() {
    var nextTheme = getEffectiveTheme() === "dark" ? "light" : "dark";
    setThemePreference(nextTheme);
  });

  if (darkModeQuery) {
    var handleSystemThemeChange = function(event) {
      if (isExplicitTheme(root.getAttribute("data-theme"))) {
        return;
      }

      syncThemeColor(event.matches ? "dark" : "light");
      syncThemeToggle();
    };

    if (typeof darkModeQuery.addEventListener === "function") {
      darkModeQuery.addEventListener("change", handleSystemThemeChange);
    } else if (typeof darkModeQuery.addListener === "function") {
      darkModeQuery.addListener(handleSystemThemeChange);
    }
  }

  syncThemeColor(getEffectiveTheme());
  syncThemeToggle();

   // Sticky footer
  var bumpIt = function() {
      $("body").css("margin-bottom", $(".page__footer").outerHeight(true));
    },
    didResize = false;

  bumpIt();

  $(window).resize(function() {
    didResize = true;
  });
  setInterval(function() {
    if (didResize) {
      didResize = false;
      bumpIt();
    }
  }, 250);
  // FitVids init
  $("#main").fitVids();

  // init sticky sidebar
  $(".sticky").Stickyfill();

  var stickySideBar = function(){
    var show = $(".author__urls-wrapper button").length === 0 ? $(window).width() > 1024 : !$(".author__urls-wrapper button").is(":visible");
    // console.log("has button: " + $(".author__urls-wrapper button").length === 0);
    // console.log("Window Width: " + windowWidth);
    // console.log("show: " + show);
    //old code was if($(window).width() > 1024)
    if (show) {
      // fix
      Stickyfill.rebuild();
      Stickyfill.init();
      $(".author__urls").show();
    } else {
      // unfix
      Stickyfill.stop();
      $(".author__urls").hide();
    }
  };

  stickySideBar();

  $(window).resize(function(){
    stickySideBar();
  });

  // Follow menu drop down

  $(".author__urls-wrapper button").on("click", function() {
    $(".author__urls").fadeToggle("fast", function() {});
    $(".author__urls-wrapper button").toggleClass("open");
  });

  // init smooth scroll
  $("a").smoothScroll({offset: -20});

  // add lightbox class to all image links
  $("a[href$='.jpg'],a[href$='.jpeg'],a[href$='.JPG'],a[href$='.png'],a[href$='.gif']").addClass("image-popup");

  // Magnific-Popup options
  $(".image-popup").magnificPopup({
    // disableOn: function() {
    //   if( $(window).width() < 500 ) {
    //     return false;
    //   }
    //   return true;
    // },
    type: 'image',
    tLoading: 'Loading image #%curr%...',
    gallery: {
      enabled: true,
      navigateByImgClick: true,
      preload: [0,1] // Will preload 0 - before current, and 1 after the current image
    },
    image: {
      tError: '<a href="%url%">Image #%curr%</a> could not be loaded.',
    },
    removalDelay: 500, // Delay in milliseconds before popup is removed
    // Class that is added to body when popup is open.
    // make it unique to apply your CSS animations just to this exact popup
    mainClass: 'mfp-zoom-in',
    callbacks: {
      beforeOpen: function() {
        // just a hack that adds mfp-anim class to markup
        this.st.image.markup = this.st.image.markup.replace('mfp-figure', 'mfp-figure mfp-with-anim');
      }
    },
    closeOnContentClick: true,
    midClick: true // allow opening popup on middle mouse click. Always set it to true if you don't provide alternative source.
  });

  $("[data-publication-index]").each(function() {
    var $root = $(this);
    var $items = $root.find("[data-publication-item]");
    var $empty = $root.find("[data-publication-empty]");
    var $typeButtons = $root.find("[data-filter-type]");
    var $yearButtons = $root.find("[data-filter-year]");
    var activeType = "all";
    var activeYear = "all";

    if ($items.length === 0 || $typeButtons.length === 0 || $yearButtons.length === 0) {
      return;
    }

    var syncButtons = function($buttons, attributeName, activeValue) {
      $buttons.each(function() {
        var $button = $(this);
        var isActive = $button.attr(attributeName) === activeValue;
        $button.toggleClass("is-active", isActive);
        $button.attr("aria-pressed", isActive ? "true" : "false");
      });
    };

    var applyFilters = function() {
      var visibleCount = 0;

      $items.each(function() {
        var $item = $(this);
        var matchesType = activeType === "all" || $item.attr("data-type") === activeType;
        var matchesYear = activeYear === "all" || $item.attr("data-year") === activeYear;
        var shouldShow = matchesType && matchesYear;

        $item.prop("hidden", !shouldShow);
        $item.attr("aria-hidden", shouldShow ? "false" : "true");

        if (shouldShow) {
          visibleCount += 1;
        }
      });

      $empty.prop("hidden", visibleCount !== 0);
      syncButtons($typeButtons, "data-filter-type", activeType);
      syncButtons($yearButtons, "data-filter-year", activeYear);
    };

    $typeButtons.on("click", function() {
      activeType = $(this).attr("data-filter-type");
      applyFilters();
    });

    $yearButtons.on("click", function() {
      activeYear = $(this).attr("data-filter-year");
      applyFilters();
    });

    applyFilters();
  });

});
