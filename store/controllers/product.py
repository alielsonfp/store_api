from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from pydantic import UUID4
from store.core.exceptions import NotFoundException

from store.schemas.product import ProductIn, ProductOut, ProductUpdate, ProductUpdateOut
from store.usecases.product import ProductUsecase
from datetime import datetime

router = APIRouter(tags=["products"])


@router.post(path="/", status_code=status.HTTP_201_CREATED)
async def post(
    body: ProductIn = Body(...), usecase: ProductUsecase = Depends()
) -> ProductOut:
    try:
        return await usecase.create(body=body)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=exc.message)


@router.get(path="/{id}", status_code=status.HTTP_200_OK)
async def get(
    id: UUID4 = Path(alias="id"), usecase: ProductUsecase = Depends()
) -> ProductOut:
    try:
        return await usecase.get(id=id)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.get(path="/", status_code=status.HTTP_200_OK)
async def query(usecase: ProductUsecase = Depends()) -> List[ProductOut]:
    return await usecase.query()

@router.get("/products/price-range", status_code=status.HTTP_200_OK)
async def fetch_products_by_price_range(
    minimum_price: float, 
    maximum_price: float, 
    product_usecase: ProductUsecase = Depends()
) -> List[ProductOut]:
    return await product_usecase.get_products_in_price_range(min_price=minimum_price, max_price=maximum_price)


@router.patch("/{id}", status_code=status.HTTP_200_OK)
async def update_product(
    id: UUID4 = Path(..., alias="id"),
    body: ProductUpdate = Body(...),
    product_service: ProductUsecase = Depends()
) -> ProductUpdateOut:
    try:
        body.updated_at = datetime.now()
        updated_product = await product_service.update(id=id, body=body)
        return updated_product
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado. Por favor, tente novamente."
        ) from e


@router.delete(path="/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    id: UUID4 = Path(alias="id"), usecase: ProductUsecase = Depends()
) -> None:
    try:
        await usecase.delete(id=id)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
