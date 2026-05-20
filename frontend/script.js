async function predictComplaint(){

    const complaint =
        document.getElementById("complaint").value;

    const loading =
        document.getElementById("loading");

    const resultBox =
        document.getElementById("resultBox");

    const result =
        document.getElementById("result");

    if(complaint.trim() === ""){

        alert("Please enter complaint");

        return;
    }

    loading.style.display = "block";

    resultBox.style.display = "none";

    try{

        const response = await fetch(

            "http://127.0.0.1:5000/predict",

            {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    complaint: complaint
                })
            }
        );

        const data = await response.json();

        loading.style.display = "none";

        resultBox.style.display = "block";

        if(data.success){

            result.innerHTML =
                data.category;

        }else{

            result.innerHTML =
                "Prediction Failed";
        }

    }catch(error){

        loading.style.display = "none";

        alert("Backend Connection Error");

        console.log(error);
    }
}