<!DOCTYPE html>
<html lang="en"><!-- InstanceBegin template="/Templates/index.dwt" codeOutsideHTMLIsLocked="false" -->
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
        <meta name="description" content="" />
        <meta name="author" content="" />
        <!-- InstanceBeginEditable name="doctitle" -->
        <title>Flask</title>
        <!-- InstanceEndEditable -->
        <!-- Favicon-->
        <link rel="icon" type="image/x-icon" href="assets/favicon.ico" />
        <!-- Bootstrap icons-->
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.5.0/font/bootstrap-icons.css" rel="stylesheet" />
        <!-- Core theme CSS (includes Bootstrap)-->
        <link href="css/styles.css" rel="stylesheet" />
    
    <!-- InstanceBeginEditable name="head" -->
    <!-- InstanceEndEditable -->
    
    </head>
    <body class="d-flex flex-column h-100">
        <main class="flex-shrink-0">
            <!-- Navigation-->
            <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
                <div class="container px-5">
                    <a class="navbar-brand" href="index.html">Start Bootstrap</a>
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation"><span class="navbar-toggler-icon"></span></button>
                    <div class="collapse navbar-collapse" id="navbarSupportedContent">
                        <ul class="navbar-nav ms-auto mb-2 mb-lg-0">
                            <li class="nav-item"><a class="nav-link" href="/var/wwww/Concept5/index.php">Home</a></li>
                            <li class="nav-item"><a class="nav-link" href="/var/wwww/Concept5/flask.php">Flask</a></li>
                            <li class="nav-item"><a class="nav-link" href="/var/wwww/Concept5/login.php">Login</a></li>
                        </ul>
                    </div>
                </div>
            </nav>
             
			<!-- Header-->
			<!-- InstanceBeginEditable name="Data" -->
            <header class="bg-dark py-5">
                <div class="container px-5">
                    <div class="row gx-5 align-items-center justify-content-center">
                        <div class="col-lg-8 col-xl-7 col-xxl-6">
                            <div class="my-5 text-center text-xl-start">
                                <h1 class="display-5 fw-bolder text-white mb-2">Een pagina met PID regeling.</h1>
                                <p class="lead fw-normal text-white-50 mb-4"></p>
                            </div>
                        </div>
                    </div>
                </div>
            </header>
            <!-- Features section-->
            <section class="py-5" id="features">
                <div class="container px-5 my-5">
                    <div class="row gx-5">
						
                        <div class="col-lg-4 mb-5 mb-lg-0"><h2 class="fw-bolder mb-0">PID.</h2></div>
						
                        <div class="col-lg-8">
                          <div class="row gx-5 row-cols-1 row-cols-md-2">
							  
                            <div class="col mb-5 h-100">
                              <h2 class="h5">De PID-Regelaar</h2>
                              <p class="mb-0"><input id="temp-slider" type="range" min="0" max="40" value="20" onchange="TempSlider(this.value)">Gewenste temperatuur</p>
                              <p class="mb-0"><input id="P-slider" type="range" min="0" max="1" value="1" onchange="PSlider(this.value)">P-waarde</p>
                              <p class="mb-0"><input id="I-slider" type="range" min="0" max="1" value="0" onchange="ISlider(this.value)">I-waarde</p>
                              <p class="mb-0"><input id="D-slider" type="range" min="0" max="1" value="0" onchange="DSlider(this.value)">D-waarde</p>

                            </div>
							  <!-- InstanceEndEditable -->
                          </div>
                        </div>
                        </div>
                </div>
            </section>
          
            
            
        </main>
           
	
			
        <!-- Footer-->
        <footer class="bg-dark py-4 mt-auto">
            <div class="container px-5">
                <div class="row align-items-center justify-content-between flex-column flex-sm-row">
                    <div class="col-auto"><div class="small m-0 text-white">Copyright &copy; Your Website 2023</div></div>
                    <div class="col-auto">
                        <a class="link-light small" href="#!">Privacy</a>
                        <span class="text-white mx-1">&middot;</span>
                        <a class="link-light small" href="#!">Terms</a>
                        <span class="text-white mx-1">&middot;</span>
                        <a class="link-light small" href="#!">Contact</a>
                    </div>
                </div>
            </div>
        </footer>
        <!-- Bootstrap core JS-->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
        <!-- Core theme JS-->
        <script src="js/scripts.js"></script>
        <script src="https://code.jquery.com/jquery-1.10.2.js"></script>
    <script>
        function TempSlider(nummer) {
            $.post("/TempSlider", { "getal": nummer });
        }
        function PSlider(nummer) {
            $.post("/PSlider", { "getal": nummer });
        }
        function ISlider(nummer) {
            $.post("/ISlider", { "getal": nummer });
        }
        function DSlider(nummer) {
            $.post("/DSlider", { "getal": nummer });
        }


        // Auto-refresh values
        window.setInterval(function () {
            $("#valueW").load("/dataoutW");
            $("#valueX").load("/dataoutX");
            $("#valueWX").load("/dataoutWX");
            $("#valueY").load("/dataoutY");
            $("#dataoutYP").load("/dataoutYP");
        }, 1000);
    </script>
    </body>
<!-- InstanceEnd --></html>
