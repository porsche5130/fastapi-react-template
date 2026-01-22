# Master-Detail 架構設計

## 概述

Master-Detail（主從式）架構是一種常見的資料關聯模式，用於處理一對多的資料關係。本文件說明如何在單一功能中設計和實作 Master-Detail 架構。

## 核心原則

1. **單一功能**：Master 和 Detail 在同一個功能（同一個 func_code）中管理
2. **單一模組**：使用同一個 module_code 處理多個資料表
3. **ORM 關聯**：在 Model 層定義資料表之間的 relationship
4. **巢狀 API**：使用巢狀路由表達 Master-Detail 關係
5. **統一 UI**：前端在同一個頁面中顯示 Master 和 Detail

## 架構設計

### 資料庫層

```
sysfunction 記錄：
  func_code = 'invoices'           → 權限識別、前端路由
  module_code = 'invoices'         → API 路由識別

模組內包含的資料表：
  - invoice (Master)
  - invoice_item (Detail)

資料表關聯：
  - invoice.id (主鍵)
  - invoice_item.invoice_id (外鍵，指向 invoice.id)
```

### API 路由設計

```
Master 路由：
  GET    /api/invoices              → 取得發票列表
  GET    /api/invoices/{id}         → 取得單一發票
  POST   /api/invoices              → 建立發票
  PUT    /api/invoices/{id}         → 更新發票
  DELETE /api/invoices/{id}         → 刪除發票

Detail 路由（巢狀）：
  GET    /api/invoices/{id}/items   → 取得發票明細列表
  POST   /api/invoices/{id}/items   → 新增發票明細
  PUT    /api/invoices/{id}/items/{item_id} → 更新發票明細
  DELETE /api/invoices/{id}/items/{item_id} → 刪除發票明細
```

## 完整實作範例：發票管理

### 1. 資料庫設計

#### sysfunction 設定

```sql
INSERT INTO sysfunction (
    func_code,              -- 'invoices'
    module_code,            -- 'invoices'
    func_cname,             -- '發票管理'
    func_ename,             -- 'Invoice Management'
    memo,                   -- '管理發票主檔及明細'
    func_order,
    func_icon,
    parent_id,
    is_active
) VALUES (
    'invoices',
    'invoices',
    '發票管理',
    'Invoice Management',
    '管理發票主檔(invoice)及明細(invoice_item)',
    100,
    '📄',
    10,  -- 假設屬於某個上層選單
    true
);
```

#### 資料表結構

```sql
-- Master 表：發票主檔
CREATE TABLE invoice (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    invoice_date DATE NOT NULL,
    customer_name VARCHAR(200) NOT NULL,
    total_amount DECIMAL(15,2) DEFAULT 0,
    tax_amount DECIMAL(15,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER
);

-- Detail 表：發票明細
CREATE TABLE invoice_item (
    id SERIAL PRIMARY KEY,
    invoice_id INTEGER NOT NULL,
    item_seq INTEGER NOT NULL,
    product_code VARCHAR(50),
    product_name VARCHAR(200) NOT NULL,
    quantity DECIMAL(15,3) NOT NULL,
    unit_price DECIMAL(15,2) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    tax_rate DECIMAL(5,2) DEFAULT 0,
    tax_amount DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_invoice
        FOREIGN KEY (invoice_id)
        REFERENCES invoice(id)
        ON DELETE CASCADE,

    CONSTRAINT uk_invoice_item
        UNIQUE (invoice_id, item_seq)
);

-- 索引
CREATE INDEX idx_invoice_item_invoice_id ON invoice_item(invoice_id);
CREATE INDEX idx_invoice_date ON invoice(invoice_date);
CREATE INDEX idx_invoice_number ON invoice(invoice_number);
```

### 2. 後端實作

#### Model 層

```python
# app/models/invoice.py
from sqlalchemy import Column, Integer, String, Date, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Invoice(Base):
    """發票主檔 Model"""
    __tablename__ = "invoice"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    invoice_date = Column(Date, nullable=False, index=True)
    customer_name = Column(String(200), nullable=False)
    total_amount = Column(Numeric(15, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    status = Column(String(20), default='draft')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer)
    updated_by = Column(Integer)

    # Relationship：一對多關聯
    items = relationship(
        "InvoiceItem",
        back_populates="invoice",
        cascade="all, delete-orphan",  # 刪除 Invoice 時自動刪除 Items
        lazy="selectin"  # 查詢 Invoice 時自動載入 Items
    )


class InvoiceItem(Base):
    """發票明細 Model"""
    __tablename__ = "invoice_item"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoice.id"), nullable=False, index=True)
    item_seq = Column(Integer, nullable=False)
    product_code = Column(String(50))
    product_name = Column(String(200), nullable=False)
    quantity = Column(Numeric(15, 3), nullable=False)
    unit_price = Column(Numeric(15, 2), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    tax_rate = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship：多對一關聯
    invoice = relationship("Invoice", back_populates="items")
```

#### Schema 層

```python
# app/schemas/invoice.py
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

# Invoice Item Schemas
class InvoiceItemBase(BaseModel):
    """發票明細基礎 Schema"""
    item_seq: int
    product_code: Optional[str] = None
    product_name: str
    quantity: Decimal
    unit_price: Decimal
    amount: Decimal
    tax_rate: Optional[Decimal] = Decimal('0')
    tax_amount: Optional[Decimal] = Decimal('0')


class InvoiceItemCreate(InvoiceItemBase):
    """建立發票明細 Schema"""
    pass


class InvoiceItemUpdate(BaseModel):
    """更新發票明細 Schema"""
    item_seq: Optional[int] = None
    product_code: Optional[str] = None
    product_name: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    amount: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None


class InvoiceItemResponse(InvoiceItemBase):
    """發票明細回應 Schema"""
    id: int
    invoice_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Invoice Schemas
class InvoiceBase(BaseModel):
    """發票基礎 Schema"""
    invoice_number: str
    invoice_date: date
    customer_name: str
    total_amount: Optional[Decimal] = Decimal('0')
    tax_amount: Optional[Decimal] = Decimal('0')
    status: Optional[str] = 'draft'


class InvoiceCreate(InvoiceBase):
    """建立發票 Schema（可包含明細）"""
    items: Optional[List[InvoiceItemCreate]] = []


class InvoiceUpdate(BaseModel):
    """更新發票 Schema"""
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    customer_name: Optional[str] = None
    total_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    status: Optional[str] = None


class InvoiceResponse(InvoiceBase):
    """發票回應 Schema（包含明細）"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    items: List[InvoiceItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


class InvoiceListResponse(InvoiceBase):
    """發票列表回應 Schema（不包含明細，提升效能）"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
```

#### Service 層

```python
# app/services/invoice_service.py
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.invoice import Invoice, InvoiceItem
from app.schemas.invoice import (
    InvoiceCreate, InvoiceUpdate,
    InvoiceItemCreate, InvoiceItemUpdate
)

class InvoiceService:
    """發票服務"""

    async def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Invoice]:
        """取得發票列表（不含明細）"""
        query = db.query(Invoice)

        if status:
            query = query.filter(Invoice.status == status)

        return query.offset(skip).limit(limit).all()

    async def get_by_id(self, db: Session, invoice_id: int) -> Invoice:
        """取得單一發票（含明細）"""
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        return invoice

    async def create(
        self,
        db: Session,
        data: InvoiceCreate,
        user_id: int
    ) -> Invoice:
        """建立發票（可同時建立明細）"""
        # 建立 Master
        invoice_data = data.model_dump(exclude={'items'})
        invoice = Invoice(**invoice_data, created_by=user_id, updated_by=user_id)

        # 建立 Detail
        if data.items:
            for item_data in data.items:
                item = InvoiceItem(**item_data.model_dump(), invoice=invoice)
                db.add(item)

        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        return invoice

    async def update(
        self,
        db: Session,
        invoice_id: int,
        data: InvoiceUpdate,
        user_id: int
    ) -> Invoice:
        """更新發票主檔"""
        invoice = await self.get_by_id(db, invoice_id)

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(invoice, key, value)

        invoice.updated_by = user_id
        db.commit()
        db.refresh(invoice)
        return invoice

    async def delete(self, db: Session, invoice_id: int) -> None:
        """刪除發票（連同明細）"""
        invoice = await self.get_by_id(db, invoice_id)
        db.delete(invoice)  # cascade 會自動刪除明細
        db.commit()

    # Detail 相關方法
    async def get_items(
        self,
        db: Session,
        invoice_id: int
    ) -> List[InvoiceItem]:
        """取得發票明細列表"""
        invoice = await self.get_by_id(db, invoice_id)
        return invoice.items

    async def create_item(
        self,
        db: Session,
        invoice_id: int,
        data: InvoiceItemCreate
    ) -> InvoiceItem:
        """新增發票明細"""
        invoice = await self.get_by_id(db, invoice_id)

        item = InvoiceItem(**data.model_dump(), invoice_id=invoice_id)
        db.add(item)
        db.commit()
        db.refresh(item)

        # 更新 Master 總金額
        await self._recalculate_totals(db, invoice)

        return item

    async def update_item(
        self,
        db: Session,
        invoice_id: int,
        item_id: int,
        data: InvoiceItemUpdate
    ) -> InvoiceItem:
        """更新發票明細"""
        invoice = await self.get_by_id(db, invoice_id)

        item = db.query(InvoiceItem).filter(
            InvoiceItem.id == item_id,
            InvoiceItem.invoice_id == invoice_id
        ).first()

        if not item:
            raise HTTPException(status_code=404, detail="Invoice item not found")

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(item, key, value)

        db.commit()
        db.refresh(item)

        # 更新 Master 總金額
        await self._recalculate_totals(db, invoice)

        return item

    async def delete_item(
        self,
        db: Session,
        invoice_id: int,
        item_id: int
    ) -> None:
        """刪除發票明細"""
        invoice = await self.get_by_id(db, invoice_id)

        item = db.query(InvoiceItem).filter(
            InvoiceItem.id == item_id,
            InvoiceItem.invoice_id == invoice_id
        ).first()

        if not item:
            raise HTTPException(status_code=404, detail="Invoice item not found")

        db.delete(item)
        db.commit()

        # 更新 Master 總金額
        await self._recalculate_totals(db, invoice)

    async def _recalculate_totals(self, db: Session, invoice: Invoice) -> None:
        """重新計算發票總金額"""
        total_amount = sum(item.amount for item in invoice.items)
        total_tax = sum(item.tax_amount for item in invoice.items)

        invoice.total_amount = total_amount
        invoice.tax_amount = total_tax
        db.commit()
```

#### Router 層

```python
# app/routes/invoices.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.dependencies import get_current_user, check_permission
from app.services.invoice_service import InvoiceService
from app.services.userlog_service import UserLogService
from app.schemas.invoice import (
    InvoiceListResponse, InvoiceResponse, InvoiceCreate, InvoiceUpdate,
    InvoiceItemResponse, InvoiceItemCreate, InvoiceItemUpdate
)
from app.models.user_detail import UserDetail

router = APIRouter()

# Master 路由

@router.get("/", response_model=List[InvoiceListResponse])
async def get_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    current_user: UserDetail = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: InvoiceService = Depends()
):
    """取得發票列表"""
    # 權限檢查
    check_permission(current_user, 'invoices', 'read')

    # 取得資料
    invoices = await service.get_all(db, skip=skip, limit=limit, status=status)

    # 記錄日誌
    log_service = UserLogService()
    await log_service.log_view(
        db, current_user.id, 'invoices',
        {'skip': skip, 'limit': limit, 'status': status}
    )

    return invoices


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    current_user: UserDetail = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: InvoiceService = Depends()
):
    """取得單一發票（含明細）"""
    check_permission(current_user, 'invoices', 'read')

    invoice = await service.get_by_id(db, invoice_id)

    log_service = UserLogService()
    await log_service.log_view(
        db, current_user.id, 'invoices', invoice, invoice_id
    )

    return invoice


@router.post("/", response_model=InvoiceResponse, status_code=201)
async def create_invoice(
    data: InvoiceCreate,
    current_user: UserDetail = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: InvoiceService = Depends()
):
    """建立發票（可同時建立明細）"""
    check_permission(current_user, 'invoices', 'create')

    invoice = await service.create(db, data, current_user.id)

    log_service = UserLogService()
    await log_service.log_create(
        db, current_user.id, 'invoices', invoice
    )

    return invoice


@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: int,
    data: InvoiceUpdate,
    current_user: UserDetail = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: InvoiceService = Depends()
):
    """更新發票主檔"""
    check_permission(current_user, 'invoices', 'update')

    original = await service.get_by_id(db, invoice_id)
    updated = await service.update(db, invoice_id, data, current_user.id)

    log_service = UserLogService()
    await log_service.log_update(
        db, current_user.id, 'invoices', original, updated
    )

    return updated


@router.delete("/{invoice_id}", status_code=204)
async def delete_invoice(
    invoice_id: int,
    current_user: UserDetail = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: InvoiceService = Depends()
):
    """刪除發票（連同明細）"""
    check_permission(current_user, 'invoices', 'delete')

    invoice = await service.get_by_id(db, invoice_id)
    await service.delete(db, invoice_id)

    log_service = UserLogService()
    await log_service.log_delete(
        db, current_user.id, 'invoices', invoice
    )


# Detail 路由（巢狀）

@router.get("/{invoice_id}/items", response_model=List[InvoiceItemResponse])
async def get_invoice_items(
    invoice_id: int,
    current_user: UserDetail = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: InvoiceService = Depends()
):
    """取得發票明細列表"""
    check_permission(current_user, 'invoices', 'read')

    items = await service.get_items(db, invoice_id)

    return items


@router.post("/{invoice_id}/items", response_model=InvoiceItemResponse, status_code=201)
async def create_invoice_item(
    invoice_id: int,
    data: InvoiceItemCreate,
    current_user: UserDetail = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: InvoiceService = Depends()
):
    """新增發票明細"""
    check_permission(current_user, 'invoices', 'create')

    item = await service.create_item(db, invoice_id, data)

    log_service = UserLogService()
    await log_service.log_create(
        db, current_user.id, 'invoices', item, f"新增明細 (Invoice #{invoice_id})"
    )

    return item


@router.put("/{invoice_id}/items/{item_id}", response_model=InvoiceItemResponse)
async def update_invoice_item(
    invoice_id: int,
    item_id: int,
    data: InvoiceItemUpdate,
    current_user: UserDetail = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: InvoiceService = Depends()
):
    """更新發票明細"""
    check_permission(current_user, 'invoices', 'update')

    updated = await service.update_item(db, invoice_id, item_id, data)

    log_service = UserLogService()
    await log_service.log_update(
        db, current_user.id, 'invoices', None, updated, f"更新明細 (Invoice #{invoice_id})"
    )

    return updated


@router.delete("/{invoice_id}/items/{item_id}", status_code=204)
async def delete_invoice_item(
    invoice_id: int,
    item_id: int,
    current_user: UserDetail = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: InvoiceService = Depends()
):
    """刪除發票明細"""
    check_permission(current_user, 'invoices', 'delete')

    await service.delete_item(db, invoice_id, item_id)

    log_service = UserLogService()
    await log_service.log_delete(
        db, current_user.id, 'invoices', None, f"刪除明細 (Invoice #{invoice_id})"
    )
```

#### 註冊路由

```python
# app/main.py
from app.routes import invoices

app.include_router(
    invoices.router,
    prefix="/api/invoices",  # 使用 module_code
    tags=["發票管理"]
)
```

### 3. 前端實作

#### TypeScript 類型定義

```typescript
// src/types/invoice.ts

export interface InvoiceItem {
  id: number;
  invoice_id: number;
  item_seq: number;
  product_code?: string;
  product_name: string;
  quantity: number;
  unit_price: number;
  amount: number;
  tax_rate: number;
  tax_amount: number;
  created_at: string;
  updated_at?: string;
}

export interface Invoice {
  id: number;
  invoice_number: string;
  invoice_date: string;
  customer_name: string;
  total_amount: number;
  tax_amount: number;
  status: string;
  created_at: string;
  updated_at?: string;
  created_by?: number;
  updated_by?: number;
  items: InvoiceItem[];
}

export interface InvoiceListItem {
  id: number;
  invoice_number: string;
  invoice_date: string;
  customer_name: string;
  total_amount: number;
  tax_amount: number;
  status: string;
  created_at: string;
  updated_at?: string;
}

export interface InvoiceCreateData {
  invoice_number: string;
  invoice_date: string;
  customer_name: string;
  total_amount?: number;
  tax_amount?: number;
  status?: string;
  items?: InvoiceItemCreateData[];
}

export interface InvoiceItemCreateData {
  item_seq: number;
  product_code?: string;
  product_name: string;
  quantity: number;
  unit_price: number;
  amount: number;
  tax_rate?: number;
  tax_amount?: number;
}
```

#### Service 層

```typescript
// src/services/invoiceService.ts
import axios from '../api/axios';
import { Invoice, InvoiceListItem, InvoiceCreateData, InvoiceItem, InvoiceItemCreateData } from '../types/invoice';

// Master API
export const getInvoices = async (params?: {
  skip?: number;
  limit?: number;
  status?: string;
}): Promise<InvoiceListItem[]> => {
  const response = await axios.get('/api/invoices/', { params });
  return response.data;
};

export const getInvoice = async (invoiceId: number): Promise<Invoice> => {
  const response = await axios.get(`/api/invoices/${invoiceId}`);
  return response.data;
};

export const createInvoice = async (data: InvoiceCreateData): Promise<Invoice> => {
  const response = await axios.post('/api/invoices/', data);
  return response.data;
};

export const updateInvoice = async (
  invoiceId: number,
  data: Partial<InvoiceCreateData>
): Promise<Invoice> => {
  const response = await axios.put(`/api/invoices/${invoiceId}`, data);
  return response.data;
};

export const deleteInvoice = async (invoiceId: number): Promise<void> => {
  await axios.delete(`/api/invoices/${invoiceId}`);
};

// Detail API
export const getInvoiceItems = async (invoiceId: number): Promise<InvoiceItem[]> => {
  const response = await axios.get(`/api/invoices/${invoiceId}/items`);
  return response.data;
};

export const createInvoiceItem = async (
  invoiceId: number,
  data: InvoiceItemCreateData
): Promise<InvoiceItem> => {
  const response = await axios.post(`/api/invoices/${invoiceId}/items`, data);
  return response.data;
};

export const updateInvoiceItem = async (
  invoiceId: number,
  itemId: number,
  data: Partial<InvoiceItemCreateData>
): Promise<InvoiceItem> => {
  const response = await axios.put(`/api/invoices/${invoiceId}/items/${itemId}`, data);
  return response.data;
};

export const deleteInvoiceItem = async (
  invoiceId: number,
  itemId: number
): Promise<void> => {
  await axios.delete(`/api/invoices/${invoiceId}/items/${itemId}`);
};
```

#### Page 元件

```typescript
// src/pages/InvoicesPage.tsx
import React, { useState, useEffect } from 'react';
import { usePermission } from '../hooks/usePermission';
import { logView, logCreate, logUpdate, logDelete } from '../services/userlogService';
import {
  getInvoices,
  getInvoice,
  createInvoice,
  updateInvoice,
  deleteInvoice,
  createInvoiceItem,
  updateInvoiceItem,
  deleteInvoiceItem
} from '../services/invoiceService';
import { Invoice, InvoiceListItem } from '../types/invoice';

const InvoicesPage: React.FC = () => {
  const { hasPermission } = usePermission();
  const [invoices, setInvoices] = useState<InvoiceListItem[]>([]);
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (hasPermission('invoices', 'read')) {
      loadInvoices();
      logView('invoices', {}, null);
    }
  }, []);

  const loadInvoices = async () => {
    setIsLoading(true);
    try {
      const data = await getInvoices();
      setInvoices(data);
    } catch (error) {
      console.error('Failed to load invoices:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectInvoice = async (invoiceId: number) => {
    try {
      const invoice = await getInvoice(invoiceId);
      setSelectedInvoice(invoice);
    } catch (error) {
      console.error('Failed to load invoice:', error);
    }
  };

  const handleCreateInvoice = async (data: any) => {
    if (!hasPermission('invoices', 'create')) {
      alert('無權限');
      return;
    }

    try {
      const created = await createInvoice(data);
      await logCreate('invoices', created);
      await loadInvoices();
      setSelectedInvoice(created);
    } catch (error) {
      console.error('Failed to create invoice:', error);
    }
  };

  const handleUpdateInvoice = async (invoiceId: number, data: any) => {
    if (!hasPermission('invoices', 'update')) {
      alert('無權限');
      return;
    }

    try {
      const original = selectedInvoice;
      const updated = await updateInvoice(invoiceId, data);
      await logUpdate('invoices', original, updated);
      await loadInvoices();
      setSelectedInvoice(updated);
    } catch (error) {
      console.error('Failed to update invoice:', error);
    }
  };

  const handleDeleteInvoice = async (invoiceId: number) => {
    if (!hasPermission('invoices', 'delete')) {
      alert('無權限');
      return;
    }

    if (!confirm('確定要刪除此發票嗎？（包含所有明細）')) {
      return;
    }

    try {
      await logDelete('invoices', selectedInvoice);
      await deleteInvoice(invoiceId);
      await loadInvoices();
      setSelectedInvoice(null);
    } catch (error) {
      console.error('Failed to delete invoice:', error);
    }
  };

  const handleAddItem = async (data: any) => {
    if (!selectedInvoice) return;

    try {
      await createInvoiceItem(selectedInvoice.id, data);
      await logCreate('invoices', data, '新增明細');
      // 重新載入發票以更新總金額和明細
      await handleSelectInvoice(selectedInvoice.id);
    } catch (error) {
      console.error('Failed to add item:', error);
    }
  };

  const handleUpdateItem = async (itemId: number, data: any) => {
    if (!selectedInvoice) return;

    try {
      await updateInvoiceItem(selectedInvoice.id, itemId, data);
      await logUpdate('invoices', null, data, '更新明細');
      await handleSelectInvoice(selectedInvoice.id);
    } catch (error) {
      console.error('Failed to update item:', error);
    }
  };

  const handleDeleteItem = async (itemId: number) => {
    if (!selectedInvoice) return;

    if (!confirm('確定要刪除此明細嗎？')) {
      return;
    }

    try {
      await deleteInvoiceItem(selectedInvoice.id, itemId);
      await logDelete('invoices', null, '刪除明細');
      await handleSelectInvoice(selectedInvoice.id);
    } catch (error) {
      console.error('Failed to delete item:', error);
    }
  };

  return (
    <div className="invoices-page">
      <h1>發票管理</h1>

      <div className="layout">
        {/* Master 列表 */}
        <div className="invoice-list">
          <button onClick={() => handleCreateInvoice({})}>新增發票</button>

          {invoices.map((invoice) => (
            <div
              key={invoice.id}
              className={`invoice-item ${selectedInvoice?.id === invoice.id ? 'active' : ''}`}
              onClick={() => handleSelectInvoice(invoice.id)}
            >
              <div>{invoice.invoice_number}</div>
              <div>{invoice.customer_name}</div>
              <div>{invoice.total_amount}</div>
            </div>
          ))}
        </div>

        {/* Master 詳細 + Detail 列表 */}
        {selectedInvoice && (
          <div className="invoice-detail">
            {/* Master 資訊 */}
            <div className="master-section">
              <h2>發票資訊</h2>
              <div>發票號碼: {selectedInvoice.invoice_number}</div>
              <div>客戶名稱: {selectedInvoice.customer_name}</div>
              <div>總金額: {selectedInvoice.total_amount}</div>
              <div>稅額: {selectedInvoice.tax_amount}</div>

              <button onClick={() => handleUpdateInvoice(selectedInvoice.id, {})}>
                編輯
              </button>
              <button onClick={() => handleDeleteInvoice(selectedInvoice.id)}>
                刪除
              </button>
            </div>

            {/* Detail 列表 */}
            <div className="detail-section">
              <h3>發票明細</h3>
              <button onClick={() => handleAddItem({})}>新增明細</button>

              <table>
                <thead>
                  <tr>
                    <th>序號</th>
                    <th>商品代碼</th>
                    <th>商品名稱</th>
                    <th>數量</th>
                    <th>單價</th>
                    <th>金額</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedInvoice.items.map((item) => (
                    <tr key={item.id}>
                      <td>{item.item_seq}</td>
                      <td>{item.product_code}</td>
                      <td>{item.product_name}</td>
                      <td>{item.quantity}</td>
                      <td>{item.unit_price}</td>
                      <td>{item.amount}</td>
                      <td>
                        <button onClick={() => handleUpdateItem(item.id, {})}>
                          編輯
                        </button>
                        <button onClick={() => handleDeleteItem(item.id)}>
                          刪除
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default InvoicesPage;
```

#### 前端路由

```typescript
// src/App.tsx
import InvoicesPage from './pages/InvoicesPage';

<Route path="invoices" element={<InvoicesPage />} />
```

## 設計總表

| 項目 | 說明 |
|-----|------|
| **func_code** | invoices |
| **module_code** | invoices |
| **前端路由** | /invoices |
| **後端 API (Master)** | /api/invoices |
| **後端 API (Detail)** | /api/invoices/{id}/items |
| **資料表** | invoice (Master)<br>invoice_item (Detail) |
| **Model** | Invoice, InvoiceItem (relationship 關聯) |
| **Schema** | InvoiceCreate, InvoiceResponse, InvoiceItemCreate, InvoiceItemResponse |
| **Service** | InvoiceService (處理 Master 和 Detail) |
| **Router** | invoices.py (包含 Master 和 Detail 路由) |
| **前端頁面** | InvoicesPage.tsx (顯示 Master 和 Detail) |

## 關鍵設計要點

### 1. ORM Relationship 配置

```python
# Master 端
class Invoice(Base):
    items = relationship(
        "InvoiceItem",
        back_populates="invoice",
        cascade="all, delete-orphan",  # 刪除 Master 時自動刪除 Detail
        lazy="selectin"  # 自動載入關聯資料
    )

# Detail 端
class InvoiceItem(Base):
    invoice_id = Column(Integer, ForeignKey("invoice.id"), nullable=False)
    invoice = relationship("Invoice", back_populates="items")
```

### 2. 巢狀 API 路由設計

```python
# Master 路由
@router.get("/")               # GET /api/invoices
@router.get("/{invoice_id}")   # GET /api/invoices/123

# Detail 路由（巢狀在 Master 之下）
@router.get("/{invoice_id}/items")              # GET /api/invoices/123/items
@router.post("/{invoice_id}/items")             # POST /api/invoices/123/items
@router.put("/{invoice_id}/items/{item_id}")    # PUT /api/invoices/123/items/456
@router.delete("/{invoice_id}/items/{item_id}") # DELETE /api/invoices/123/items/456
```

### 3. Cascade Delete

```python
# 使用 cascade="all, delete-orphan"
# 刪除 Invoice 時自動刪除所有關聯的 InvoiceItem
await service.delete(db, invoice_id)  # 會自動刪除所有明細
```

### 4. 資料一致性

```python
# Detail 異動時自動更新 Master 總金額
async def _recalculate_totals(self, db: Session, invoice: Invoice) -> None:
    total_amount = sum(item.amount for item in invoice.items)
    total_tax = sum(item.tax_amount for item in invoice.items)
    invoice.total_amount = total_amount
    invoice.tax_amount = total_tax
    db.commit()
```

### 5. 權限檢查

```python
# 所有操作都使用同一個 func_code 檢查權限
check_permission(current_user, 'invoices', 'read')    # Master 和 Detail 都用 'invoices'
check_permission(current_user, 'invoices', 'create')
check_permission(current_user, 'invoices', 'update')
check_permission(current_user, 'invoices', 'delete')
```

### 6. 日誌記錄

```python
# Master 操作
await log_service.log_create(db, user_id, 'invoices', invoice)

# Detail 操作（加註說明）
await log_service.log_create(
    db, user_id, 'invoices', item, f"新增明細 (Invoice #{invoice_id})"
)
```

## 優點

1. **清晰的關聯結構**：透過 ORM relationship 明確定義資料關聯
2. **RESTful 設計**：使用巢狀路由清楚表達 Master-Detail 關係
3. **資料一致性**：Cascade delete 確保刪除 Master 時自動清理 Detail
4. **統一權限管理**：Master 和 Detail 使用同一個 func_code
5. **良好的 UI/UX**：在同一個頁面中操作 Master 和 Detail

## 注意事項

1. **Foreign Key 約束**：確保 Detail 表有正確的外鍵約束
2. **Cascade 設定**：根據業務需求決定是否使用 cascade delete
3. **效能考量**：列表查詢時避免載入 Detail（使用不同的 Response Schema）
4. **交易處理**：Master 和 Detail 的建立/更新應該在同一個 transaction 中
5. **錯誤處理**：Detail 操作時要先確認 Master 存在

## 更新紀錄

- 2026-01-21: 初始版本建立，完整的 Master-Detail 設計文件
- 2026-01-21: 包含資料庫、後端、前端的完整實作範例
