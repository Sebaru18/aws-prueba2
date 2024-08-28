from flask import Flask, render_template_string, jsonify, request 

import boto3 

  

app = Flask(__name__) 

s3 = boto3.client('s3') 

  

@app.route('/') 

def index(): 

    # Obtener la lista de buckets 

    response = s3.list_buckets() 

    buckets = response.get('Buckets', []) 

    # Crear una lista de nombres y metadatos de buckets 

    bucket_info = [ 

        { 

            'Name': bucket['Name'], 

            'CreationDate': str(bucket['CreationDate'])  # Convertir a string para el JSON 

        } 

        for bucket in buckets 

    ] 

    # Renderizar la lista en un HTML con JavaScript para la funcionalidad plegable 

    html = ''' 

    <!DOCTYPE html> 

    <html lang="en"> 

    <head> 

        <meta charset="UTF-8"> 

        <meta name="viewport" content="width=device-width, initial-scale=1.0"> 

        <title>S3 Buckets</title> 

        <style> 

            .bucket-info, .bucket-objects { 

                display: none; 

                padding-left: 20px; 

                border-left: 1px solid #ccc; 

            } 

            .bucket-name { 

                cursor: pointer; 

                color: #007bff; 

            } 

            .bucket-name:hover { 

                text-decoration: underline; 

            } 

            .object-name { 

                cursor: pointer; 

                color: #007bff; 

            } 

            .object-name:hover { 

                text-decoration: underline; 

            } 

        </style> 

    </head> 

    <body> 

        <h1>Lista de Buckets S3</h1> 

        <div id="bucket-list"> 

            {% for bucket in buckets %} 

            <div> 

                <div class="bucket-name" onclick="toggleBucket('{{ bucket.Name }}')">{{ bucket.Name }}</div> 

                <div id="info-{{ bucket.Name }}" class="bucket-info"> 

                    <p><strong>Creation Date:</strong> {{ bucket.CreationDate }}</p> 

                    <div id="objects-{{ bucket.Name }}" class="bucket-objects"></div> 

                </div> 

            </div> 

            {% endfor %} 

        </div> 

        <script> 

            function toggleBucket(bucketName) { 

                var infoDiv = document.getElementById('info-' + bucketName); 

                var objectsDiv = document.getElementById('objects-' + bucketName); 

                if (infoDiv.style.display === 'none' || infoDiv.style.display === '') { 

                    infoDiv.style.display = 'block'; 

                    if (objectsDiv.innerHTML === '') { 

                        fetch('/bucket-objects?bucket_name=' + encodeURIComponent(bucketName)) 

                            .then(response => response.json()) 

                            .then(data => { 

                                if (data.objects) { 

                                    var html = '<ul>'; 

                                    data.objects.forEach(object => { 

                                        html += '<li class="object-name">' + object + '</li>'; 

                                    }); 

                                    html += '</ul>'; 

                                    objectsDiv.innerHTML = html; 

                                } else { 

                                    objectsDiv.innerHTML = '<p>No objects found.</p>'; 

                                } 

                                objectsDiv.style.display = 'block'; 

                            }); 

                    } else { 

                        objectsDiv.style.display = 'block'; 

                    } 

                } else { 

                    infoDiv.style.display = 'none'; 

                    objectsDiv.style.display = 'none'; 

                } 

            } 

        </script> 

    </body> 

    </html> 

    ''' 

    return render_template_string(html, buckets=bucket_info) 

  

@app.route('/json') 

def json_view(): 

    # Obtener la lista de buckets 

    response = s3.list_buckets() 

    buckets = response.get('Buckets', []) 

    # Crear una lista de nombres de buckets 

    bucket_names = [bucket['Name'] for bucket in buckets] 

    # Devolver la lista de nombres en formato JSON 

    return jsonify(buckets=bucket_names) 

  

@app.route('/bucket-objects') 

def bucket_objects(): 

    bucket_name = request.args.get('bucket_name') 

    if not bucket_name: 

        return jsonify({'error': 'Bucket name is required'}), 400 

    try: 

        response = s3.list_objects_v2(Bucket=bucket_name) 

        objects = [obj['Key'] for obj in response.get('Contents', [])] 

        return jsonify({'objects': objects}) 

    except Exception as e: 

        return jsonify({'error': str(e)}), 500 

  

if __name__ == '__main__': 

    app.run(debug=True) 