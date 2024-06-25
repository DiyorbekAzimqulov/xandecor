from django.shortcuts import render


def sales_doctor(request):
    # Placeholder for actual data, replace with your data source
    data = [
        {"No": 1, "Name": 332, "total_received": 72, "prixot_received": 72, "prixot_salled": 36, "prixot_moving": 36, "prixot_left": 36, "urixzor_received": 36, "urixzor_salled": 36, "urixzor_moving": 36, "urixzor_left": 36, "jome_received": 36, "jome_salled": 36, "jome_moving": 36, "jome_left": 36, "bekTop_received": 36, "bekTop_salled": 36, "bekTop_moving": 36, "bekTop_left": 36, "quyliq_received": 36, "quyliq_salled": 36, "quyliq_moving": 36, "quyliq_left": 36, "total_base": 86},
        # Add more rows as needed
    ]
    
    return render(request, 'sales_doctor.html', {'data': data})