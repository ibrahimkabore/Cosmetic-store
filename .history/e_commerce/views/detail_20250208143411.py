def Detail (request,pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'home/detail.html', {'product': product})

